import logging
import sys
import requests
import os

from flask import Flask, jsonify

# Setup tasks
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logging.getLogger("requests").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

#
# App Routing
#

@app.route("/<owner>/<repo>")
def repo_sync(owner, repo):
    info = sync_repo(owner, repo)

    return jsonify(info)

#
# Helper Functions
#

def sync_repo(owner, repo):
    """
    Calls Github API to get all issues for a repository
    Pulls relevent data for sentiment processing out of each issue
    Processes each issue for sentiment
    Persists data to db
    """

    url = "https://api.github.com/repos/{}/{}/issues?state=all&per_page=100".format(owner, repo)

    response = call_github_api(url)

    while True:
        response_data = response.json()

        if response_data == None or len(response_data) == 0:
            break

        for issue in response_data:
            process_issue(issue)
            logger.info("[{}/{}] Processed Issue #{}".format(owner, repo, issue["number"]))

        if "next" in response.links.keys():
            response = call_github_api(response.links["next"]["url"])
        else:
            break

    return {
        "done": "{}/{} Processed".format(owner, repo)
    }

def process_issue(issue):
    """
    Uses Github API to get all issues for a repository
    Pulls issues 100 at a time until all issues are collected
    """
    response = call_github_api(issue["comments_url"])
    issue_comments = []
    while True:
        response_data = response.json()

        if response_data == None or len(response_data) == 0:
            break

        for comment in response_data:
            process_comment(comment)

        if "next" in response.links.keys():
            response = call_github_api(response.links["next"]["url"])
        else:
            break

    is_pr = True if "pull_request" in issue.keys() else False

    return {
        'user_name': issue["user"]["login"],
        'user_id': issue["user"]["id"],
        'number': issue["number"],
        'state': issue["state"],
        'is_pr': is_pr,
        'title': {
            'raw_text': issue["title"],
            'sentiment': get_sentiment_analysis(issue["title"])
        },
        'body': {
            'raw_text': issue["body"],
            'sentiment': get_sentiment_analysis(issue["body"])
        },
        'comments': issue_comments
    }

def process_comment(comment):
    return {
        'user_name': comment["user"]["login"],
        'user_id': comment["user"]["id"],
        'body': {
            'raw_text': comment["body"],
            'sentiment': get_sentiment_analysis(comment["body"])
        }
    }

def get_sentiment_analysis(text):
    url = "http://localhost:5001/analyze"

    response = requests.post(url, json={"text": text})

    if response.status_code != 200:
        logger.error("Sentiment could not be retrieved (Response Code: {})".format(response.status_code))
        return None

    return response.json()


def call_github_api(url):
    # TODO: Get a better token?
    token = os.environ["GH_API_TOKEN"]

    response = requests.get(url, auth=('token', token))

    # TODO: Handle rate limiting

    return response

    # if response.status_code != 200:
    #     logger.error("Error retrieving data from GitHub (Response Code: {})".format(response.status_code))
    #     return None
    #
    # return response.json()

# Flask start
if __name__ == "__main__":
    app.run(port=5000)
