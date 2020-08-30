from pymongo import MongoClient, DESCENDING
from flask import current_app, g
from werkzeug.local import LocalProxy


class MongoDB(object):
    def __init__(self):
        self.client = MongoClient(current_app.config['MONGO_URI'])
        self.db = self.client.home_inventory_db

        # Set index to enforce uniquness
        self.db['users'].create_index([('username', DESCENDING)], unique=True)

        print('created DB instance')

    def find_all(self, selector, projection=None, collection="users"):
        return self.db[collection].find(
            selector,
            projection=None,
        )

    def find(self, selector, projection=None, collection="users"):
        print('looking for ', selector)
        return self.db[collection].find_one(selector, projection=projection)

    def create(self, document, collection="users"):
        return self.db[collection].insert_one(document)

    def update(self,
               selector,
               update,
               upsert=False,
               array_filters=None,
               collection="users"):
        '''pymongo only offers update_one and update_many'''
        print("db update called")
        result = None
        cmd = None
        if upsert:
            # ID if upserted, None otherwise
            cmd = lambda: self.db[collection].update_one(
                selector, update, upsert=upsert, array_filters=array_filters
            ).upserted_id
        else:
            # 1 if modified, 0 otherwise
            cmd = lambda: self.db[collection].update_one(
                selector, update, array_filters=array_filters)
        try:
            result = cmd()
        except Exception as err:
            print("update err", err)

        return result

    def delete(self, selector, collection="users"):
        return self.db[collection].delete_one(selector).deleted_count

    def drop(self, collection="users"):
        self.db["users"].drop()
        self.db[collection].drop()


def get_db():
    if 'db' not in g:
        g.db = MongoDB()

    return g.db


db = LocalProxy(get_db)