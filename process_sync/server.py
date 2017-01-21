import logging
import sys
import requests
import os

from flask import Flask, jsonify

# Setup tasks
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
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
    issue_collection = []
    page = 1
    while True:
        issues_url = "https://api.github.com/repos/{}/{}/issues?state=all&per_page=100&page={}".format(owner, repo, page)
        new_issues = call_github_api(issues_url)

        if new_issues == None or len(new_issues) == 0:
            break

        for issue in new_issues:
            issue_collection.append(process_issue(issue))

        logger.info("[{}/{}] {} issues processed (Size {} bytes)".format(owner, repo, len(issue_collection), sys.getsizeof(issue_collection)))

        page += 1

    return issue_collection

def process_issue(issue):
    """
    Uses Github API to get all issues for a repository
    Pulls issues 100 at a time until all issues are collected
    """
    issue_comments = []
    page = 1
    while len(issue_comments) < issue["comments"]:
        comments = call_github_api("{}?per_page=100&page={}".format(issue["comments_url"], page))

        if comments == None or len(comments) == 0:
            break

        for comment in comments:
            issue_comments.append(process_comment(comment))

        logger.info("{} comments processed (Size {} bytes)".format(len(issue_comments), sys.getsizeof(issue_comments)))
        page += 1

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

    if response.status_code != 200:
        logger.error("Error retrieving data from GitHub (Response Code: {})".format(response.status_code))
        return None

    return response.json()

# Flask start
if __name__ == "__main__":
    app.run(port=5000)
