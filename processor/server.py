import logging
import sys
import os
import time
import math

import requests
import rethinkdb as r
from jsonschema import validate, FormatChecker, ValidationError

import schema

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logging.getLogger("requests").setLevel(logging.WARNING)
logger = logging.getLogger("sentimentr_bot")

# Rethink DB Setup
RDB_HOST = "localhost"
RDB_PORT = 28015

# Queue DB
QUEUE_DB = "queue"
QUEUE_TABLE = "jobs"
QUEUE_INDEX = "updated_on"

# Sentiment Storage DB
SENTIMENT_DB = "sentiment"
SENTIMENT_TABLE = "analyzed_issues"
SENTIMENT_INDEX = "repo"

# Sentiment Analysis API
ANALYSIS_ENDPOINT = os.environ["ANALYSIS_ENDPOINT"]

# GitHub API
GH_API_TOKEN = os.environ["GH_API_TOKEN"]

def process_repo(repo, connection):
    """
    Calls Github API to get all issues for a repository
    Pulls relevent data for sentiment processing out of each issue
    Processes each issue for sentiment
    Persists data to db
    """

    url = "https://api.github.com/repos/{}/issues?state=all&per_page=100".format(repo)

    response = call_github_api(url)

    while True:
        response_data = response.json()

        if response_data == None or len(response_data) == 0:
            break

        for issue in response_data:
            processed_issue = process_issue(repo, issue)
            logger.info("[{}] Processed Issue #{}".format(repo, processed_issue["number"]))
            store_issue(processed_issue, connection)
            logger.info("[{}] Stored Issue #{}".format(repo, processed_issue["number"]))

        if "next" in response.links.keys():
            response = call_github_api(response.links["next"]["url"])
        else:
            break

def process_issue(repo, issue):
    """
    Given an issue in GitHub API v3 format, process it, and it's comments for
    sentiment.
    Builds a simplified issue object using the sentiment data.
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

    title_sentiment = get_sentiment_analysis(issue["title"])
    body_sentiment = get_sentiment_analysis(issue["body"])

    processed_issue = {
        'repo': repo,
        'user': {
            'name': issue["user"]["login"],
            'id': issue["user"]["id"]
        },
        'number': issue["number"],
        'state': issue["state"],
        'is_pr': is_pr,
        'title': {
            'raw_text': issue["title"],
            'sentiment': title_sentiment
        },
        'body': {
            'raw_text': issue["body"],
            'sentiment': body_sentiment
        },
        'comments': issue_comments
    }

    return processed_issue

def process_comment(comment):
    """
    Given a comment in GitHub API v3 format, processes it for sentiment
    and returns a simplified version with only the data that we care about
    """
    body_sentiment = get_sentiment_analysis(comment["body"])

    processed_comment = {
        'user': {
            'name': comment["user"]["login"],
            'id': comment["user"]["id"]
        },
        'body': {
            'raw_text': comment["body"],
            'sentiment': body_sentiment
        }
    }

    return processed_comment

def get_sentiment_analysis(text):
    """
    Handles calls to the Sentiment Analysis backing service
    Could be swapped out which is why the processing doesn't just happen here
    If processing fails for some reason the None value is returned
    """
    response = requests.post(ANALYSIS_ENDPOINT, json={"text": text})

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
    token = os.environ["GH_API_TOKEN"]

    while True:
        response = requests.get(url, auth=('token', GH_API_TOKEN))

        if response.status_code == 200:
            return response

        if response.headers['X-RateLimit-Remaining'] == '0':
            sleep_time = int(math.ceil(int(response.headers['X-RateLimit-Reset']) - time.time()))
            logger.info("Rate Limit hit. Waiting {} seconds before trying again".format(sleep_time))
            time.sleep(sleep_time)

        if response.status_code != 200:
            logger.error("Whoa...having problems calling the GitHub API")
            logger.error("Url: {}".format(url))
            logger.error("Status Code: {}".format(response.status_code))
            logger.error("Headers: {}".format(response.headers))
            time.sleep(RETRY_LENGTH)

def store_issue(issue, connection):
    """
    Inserts or updates an issue in the SENTIMENT_DB
    """
    #TODO: HAndle updates
    r.db(SENTIMENT_DB).table(SENTIMENT_TABLE).insert(issue).run(connection)

def obtain_db_conn(host, port, retry_length):
    """
    Gets a connection. Continuously retries until it is successful
    """
    while True:
        try:
            db_conn = r.connect(host=host, port=port)
            return db_conn
        except:
            logger.info("RethinkDB not found at [host={}, port={}], retrying in {} seconds".format(host, port, retry_length))
            time.sleep(retry_length)

def db_setup(connection):
    """
    Sets up a RethinkDB for Job Queue and Sentiment storage
    Creates any dbs/tables/queues that don't exist
    """
    try:
        r.db_create(QUEUE_DB).run(connection)
        logger.info("Queue DB created")
    except:
        logger.info("Queue DB already exists")
    try:
        r.db(QUEUE_DB).table_create(QUEUE_TABLE).run(connection)
        logger.info("Queue Table created")
    except:
        logger.info("Queue Table already exists")
    try:
        r.db(QUEUE_DB).table(QUEUE_TABLE).index_create(QUEUE_INDEX).run(connection)
        r.db(QUEUE_DB).table(QUEUE_TABLE).index_wait(QUEUE_INDEX).run(connection)
        logger.info("Queue Index created")
    except:
        logger.info("Queue Index already exists".format(QUEUE_INDEX))

    logger.info("Queue DB and Table set up, ready to consume")

    # Sets up the Sentiment DB for storage of sentiment data collected
    try:
        r.db_create(SENTIMENT_DB).run(connection)
        logger.info("Sentiment DB created")
    except:
        logger.info("Sentiment DB already exists")
    try:
        r.db(SENTIMENT_DB).table_create(SENTIMENT_TABLE).run(connection)
        logger.info("Sentiment Table created")
    except:
        logger.info("Sentiment Table already exists")
    try:
        r.db(SENTIMENT_DB).table(SENTIMENT_TABLE).index_create(SENTIMENT_INDEX).run(connection)
        r.db(SENTIMENT_DB).table(SENTIMENT_TABLE).index_wait(SENTIMENT_INDEX).run(connection)
        logger.info("Sentiment Index created")
    except:
        logger.info("Sentiment Index already exists".format(SENTIMENT_INDEX))

    logger.info("Sentiment DB and Table set up, ready to get some data")

#
# Main program
#

# Initial DB Setup
db_conn = obtain_db_conn(RDB_HOST, RDB_PORT, 1)
db_setup(db_conn)

# Main program "loop"
# Subscribes to changes in the Job Queue while also taking into account anything that was already there
# Since changes can come in many types each change is validated against the job schema before processing
job_feed = r.db(QUEUE_DB).table(QUEUE_TABLE).order_by(index=QUEUE_INDEX).limit(10).changes(include_initial=True).run(db_conn)
for change in job_feed:
    try:
        validate(change, schema.JOB, format_checker=FormatChecker())
    except ValidationError as e:
        logger.info("Nothing to process or malformed: {}".format(change))
        continue

    repo_to_process = change["new_val"]["repo"]

    logger.info("Processing repository: {}".format(repo_to_process))
    process_repo(repo_to_process, db_conn)
    logger.info("Processed repository: {}".format(repo_to_process))

    r.db(QUEUE_DB).table(QUEUE_TABLE).get(change["new_val"]["id"]).delete().run(db_conn)
