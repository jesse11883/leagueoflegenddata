# from os import environ
# import redis
# from t import ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET, APP_SECRET_KEY
# from t import MONGODB_SERVER,MONGODB_PORT,MONGODB_DBNAME
# from t import REMOTE_HOST, REMOTE_PORT, REMOTE_BINDING_ADDR, REMOTE_BINDING_PORT, REMOTE_USER, REMOTE_PASS
# from t import USER_COLLECTION, FOLLOW_COLLECTION, TWEET_COLLECTION
import t

class Config(object):
    def __init__(self):
        for k, value in vars(Config).items():
        #for k in args:
            if (k not in ["__dict__", "__module__", "__init__", "__getitem__", "__weakref__"]):
                print(k, value)
                setattr(self, k, value)
            
    def __getitem__(self, item):
        return getattr(self, item)
    
    
    DEBUG = False
    TESTING = False
    MONGODB_SERVER = '192.168.1.206'
    MONGODB_PORT = 27020
    REMOTE_BINDING_ADDR = '127.0.0.1'
    REMOTE_BINDING_PORT =27020
    REMOTE_HOST = '76.244.39.101'
    REMOTE_PORT = 6824
    REMOTE_DB = t.REMOTE_DB
    REMOTE_USER = t.REMOTE_USER
    REMOTE_PASS = t.REMOTE_PASS

    MONGODB_DBNAME="loldata"
    SUMMONER_COLLECTION="summoner"
    MATCH_LIST_COLLECTION="match_list"
    MATCH_TIMELINE_COLLECTION="match_timeline"
    MATCH_DETAIL_COLLECTION="match_detail"

    
    #SECRET_KEY = APP_SECRET_KEY
    #FLASK_APP = environ.get('FLASK_APP')
    #FLASK_ENV = environ.get('FLASK_ENV')

    # Flask-Session
    #SESSION_TYPE = environ.get('SESSION_TYPE')
    #SESSION_TYPE = "redis"
    #SESSION_REDIS = redis.from_url(environ.get('SESSION_REDIS'))

class ProductionConfig(Config):
    DEBUG = False

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True