import os, datetime


class Config(object):
    '''
    Configuration of application, default is for DEVELOPMENT
    '''
    DEBUG = True

    # Set URI, the location of the app's database
    # MONGO_URI = os.environ.get('DATABASE_URL') or \
    #     'mongodb://' + 'localhost:27017'

    MONGO_URI = os.environ.get('DATABASE_URL') or \
        'mongodb://' + 'localhost:27017' or \
        'mongodb://' + 'ec2-34-227-149-36.compute-1.amazonaws.com'

    # JWT, hopefully an easy way to do auth
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    JWT_REFRESH_TOKEN_EXPIRES = datetime.timedelta(days=3)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
