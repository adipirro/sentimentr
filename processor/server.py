import logging
import os
import time
import math

import requests

import model


# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logging.getLogger("requests").setLevel(logging.WARNING)
logger = logging.getLogger("sentimentr_bot")

# Sentiment Analysis API
ANALYSIS_DOMAIN = os.getenv("ANALYSIS_DOMAIN", "localhost:5000")

# GitHub API
GH_API_TOKEN = os.getenv("GH_API_TOKEN", None)
GH_RETRY_LENGTH = os.getenv("GH_RETRY_LENGTH", 5)

def process_repo(repo):
    """
    Calls Github API to get all issues for a repository
    Pulls relevent data for sentiment processing out of each issue
    Processes each issue for sentiment
    Persists data to db
    """
    url = "https://api.github.com/repos/{}/issues?state=all&sort=updated&direction=asc&per_page=100".format(repo)

    repo_info = model.get_repo(repo)
    if repo_info:
        url += "&since={}".format(repo_info["last_update_dt"])
        logger.info("[{}] Syncing from last update date: {}".format(repo, repo_info["last_update_dt"]))
    else:
        logger.info("[{}] Repo has not been created yet. Creating.".format(repo))

        repo_info_url = "https://api.github.com/repos/{}".format(repo)
        response = call_github_api(repo_info_url)

        repo_info = response.json()

        model.store_user({
            "id": repo_info["owner"]["id"],
            "login": repo_info["owner"]["login"]
        })

        model.store_repo({
            "id": repo_info["id"],
            "user_id": repo_info["owner"]["id"],
            "full_name": repo,
            "last_update_dt": "1900-01-01T00:00:00Z"
        })

    response = call_github_api(url)

    while True:
        response_data = response.json()

        if response_data == None or len(response_data) == 0:
            break

        for issue in response_data:
            process_issue(repo_info["full_name"], repo_info["id"], issue)

        if "next" in response.links.keys():
            response = call_github_api(response.links["next"]["url"])
        else:
            break

def process_issue(repo_name, repo_id, issue):
    """
    Given an issue in GitHub API v3 format, process it, and it's comments for
    sentiment.
    Builds a simplified issue object using the sentiment data.
    """
    response = call_github_api(issue["comments_url"])

    while True:
        response_data = response.json()

        if response_data == None or len(response_data) == 0:
            break

        for comment in response_data:
            process_comment(issue['id'], comment)

        if "next" in response.links.keys():
            response = call_github_api(response.links["next"]["url"])
        else:
            break

    is_pr = True if "pull_request" in issue.keys() else False

    title_sentiment = get_sentiment_analysis(issue["title"])
    body_sentiment = get_sentiment_analysis(issue["body"])

    processed_issue = {
        'id': issue['id'],
        'repo_id': repo_id,
        'user_id': issue["user"]["id"],
        'number': issue["number"],
        'state': issue["state"],
        'is_pr': is_pr,
        'title': {
            'raw_text': issue["title"] or "",
            'sentiment': title_sentiment
        },
        'body': {
            'raw_text': issue["body"] or "",
            'sentiment': body_sentiment
        }
    }

    model.store_user({
        "id": issue["user"]["id"],
        "login": issue["user"]["login"]
    })

    model.store_issue(processed_issue)

    model.update_last_update_dt(repo_id, issue["updated_at"])

    logger.info("[{}] Processed Issue #{}".format(repo_name, processed_issue["number"]))

def process_comment(issue_id, comment):
    """
    Given a comment in GitHub API v3 format, processes it for sentiment
    and returns a simplified version with only the data that we care about
    """
    body_sentiment = get_sentiment_analysis(comment["body"])

    processed_comment = {
        'id': comment['id'],
        'issue_id': issue_id,
        'user_id': comment["user"]["id"],
        'body': {
            'raw_text': comment["body"] or "",
            'sentiment': body_sentiment
        }
    }

    model.store_user({
        "id": comment["user"]["id"],
        "login": comment["user"]["login"]
    })

    model.store_comment(processed_comment)

def get_sentiment_analysis(text):
    """
    Handles calls to the Sentiment Analysis backing service
    Could be swapped out which is why the processing doesn't just happen here
    If processing fails for some reason the None value is returned
    """
    url = "http://{}/analyze".format(ANALYSIS_DOMAIN)
    response = requests.post(url, json={"text": text})

    if response.status_code != 200:
        logger.error("Sentiment could not be retrieved (Response Code: {})".format(response.status_code))
        logger.error("Text: {}".format(text))
        return None

    return response.json()


def call_github_api(url):
    """
    Handles calls to the GitHub API
    Sleeps if the rate limit is reached ()
    Retries if any other errors occur
    """

    while True:
        if GH_API_TOKEN:
            response = requests.get(url, auth=('token', GH_API_TOKEN))
        else:
            response = requests.get(url)

        if response.status_code == 200:
            return response

        if int(response.headers['X-RateLimit-Remaining']) == 0:
            sleep_time = int(math.ceil(int(response.headers['X-RateLimit-Reset']) - time.time()))
            logger.info("Rate Limit hit. Waiting {} seconds before trying again".format(sleep_time))
            # So it turns out in some situations this can actually be a negative number
            # Take the absolute value to ensure we don't sleep for a negative amount of seconds
            time.sleep(abs(sleep_time))
        elif response.status_code != 200:
            logger.error("Whoa...having problems calling the GitHub API")
            logger.error("Url: {}".format(url))
            logger.error("Status Code: {}".format(response.status_code))
            logger.error("Headers: {}".format(response.headers))
            logger.error("JSON: {}".format(response.json()))
            time.sleep(GH_RETRY_LENGTH)

#
# Main program
#

# Initial DB Setup
model.db_setup()

# Main program "loop"
# Subscribes to changes in the Job Queue
for job in model.get_job_feed():
    repo_to_process = job["repo"]

    logger.info("Processing repository: {}".format(repo_to_process))
    process_repo(repo_to_process)
    logger.info("Processed repository: {}".format(repo_to_process))

    model.delete_job(job["id"])
