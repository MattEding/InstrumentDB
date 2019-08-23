import json
import os
from importlib import resources
from urllib import parse

import pymongo


def format_url(url, params):
    url_parts = list(parse.urlparse(url))
    query = dict(parse.parse_qsl(url_parts[4]))
    query.update(params)
    url_parts[4] = parse.urlencode(query)
    return parse.urlunparse(url_parts)


def get_mongo_client(db_username, db_password, dbarn, db_tsl=True):
    base = f'mongodb://{db_username}:{db_password}@{dbarn}.com:27017/'
    params = dict(
        replicaSet='rs0',
        readPreference='secondaryPreferred',
    )
    if db_tsl:
        extra = dict(
            ssl='true',
            ssl_ca_certs='rds-combined-ca-bundle.pem',
        )
        params.update(extra)
    return format_url(base, params)


def insert_data(collection):
    with resources.path('instruments.data.json', 'model.json') as json_file:
        pass

    with open(json_file) as fp:
        for line in fp.readlines():
            data = json.loads(line)
            collection.insert_one(data)


def main():
    db_username = os.getenv('GIBSON_DB_USERNAME')
    db_password = os.getenv('GIBSON_DB_PASSWORD')
    db_arn = os.getenv('GIBSON_DB_ARN')
    db_tsl = os.getenv('GIBSON_DB_TSL')

    if all(env is not None for env in [db_username, db_password, db_arn, db_tsl]):
        client = get_mongo_client(db_username, db_password, db_arn, db_tsl=db_tsl)
    else:
        client = pymongo.MongoClient('mongodb://localhost:27017/')
    
    db = client['instruments']
    col = db['gibson']
    insert_data(col)
    client.close()
