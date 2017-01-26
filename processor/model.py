import os
import logging
from collections import namedtuple

import rethinkdb as r
from rethinkdb.errors import ReqlNonExistenceError

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("sentimentr_model")

# Rethink DB Settings
RDB_HOST = os.getenv("RDB_HOST", "localhost")
RDB_PORT = os.getenv("RDB_PORT", 28015)
RDB_DB = os.getenv("RDB_DB", "sentimentr")
RECONNECT_TIME = os.getenv("RECONNECT_TIME", 1)

Table = namedtuple("Table", ["name", "indicies"])

JOBS = Table("jobs", ["inserted_at"])
ISSUES = Table("issues", ["repo", "updated_at", "number", "username"])
COMMENTS = Table("comments", ["issue_id", "username"])

TABLES = [JOBS, ISSUES, COMMENTS]

def connection():
    return r.connect(host=RDB_HOST, port=RDB_PORT, db=RDB_DB)

def get_job_feed():
    with connection() as conn:
        feed = r.table(JOBS.name).order_by(index="inserted_at").limit(1).changes(include_initial=True, include_types=True).run(conn)

        for job in feed:
            yield job

def delete_job(id):
    with connection() as conn:
        return r.table(JOBS.name).get(id).delete().run(conn)

def get_last_update_dt(repo):
    with connection() as conn:
        try:
            return r.table(ISSUES.name).get_all(repo, index="repo")["updated_at"].max().run(conn)
        except ReqlNonExistenceError:
            return None
        except:
            logger.exception("Hey! You probably dun goofed a bit on the query :/")

def store_issue(issue):
    if issue == None:
        return None
    with connection() as conn:
        return r.table(ISSUES.name).insert(issue, conflict="replace").run(conn)

def store_comment(comment):
    with connection() as conn:
        return r.table(COMMENTS.name).insert(comment, conflict="replace").run(conn)

def db_setup():
    """
    Sets up a RethinkDB instance for Job Queue and Sentiment storage
    Creates any dbs/tables/indicies that don't exist
    """
    def create_db(db, connection):
        try:
            r.db_create(db).run(connection)
            logger.info("DB '{}' created".format(db))
        except:
            logger.info("DB '{}' already exists".format(db))

    def create_table(db, table, connection):
        try:
            r.db(db).table_create(table).run(connection)
            logger.info("Table '{}.{}' created".format(db,table))
        except:
            logger.info("Table '{}.{}' already exists".format(db, table))

    def create_index(db, table, index, connection):
        try:
            r.db(db).table(table).index_create(index).run(connection)
            r.db(db).table(table).index_wait(index).run(connection)
            logger.info("Index '{}' created for table '{}.{}'".format(index, db, table))
        except:
            logger.info("Index '{}' already exists for table '{}.{}'".format(index, db, table))

    while True:
        try:
            conn = r.connect(host=RDB_HOST, port=RDB_PORT)
            break
        except:
            logger.info("RethinkDB not found at [host={}, port={}], retrying in {} seconds".format(RDB_HOST, RDB_PORT, RECONNECT_TIME))
            time.sleep(RECONNECT_TIME)

    create_db(RDB_DB, conn)

    for table in TABLES:
        create_table(RDB_DB, table.name, conn)

        for index in table.indicies:
            create_index(RDB_DB, table.name, index, conn)

    conn.close()
