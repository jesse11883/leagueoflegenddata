from sshtunnel import SSHTunnelForwarder

import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.json_util import dumps
import logging
from datetime import datetime


logger = logging.getLogger("loldata")


class DBConnection:

    def __init__(self, args, config):
        self.args = args
        self.config = config
        self.db = None 
        self.docol = None
        self.data_source = {}
        self.connection = {}
        logger.debug(f"X8DBConnection is created. pyMongo Version is : {pymongo.version}")
        

    def get_ds(self, ds_name, col_name = "COLLECTION"):
        logger.debug(f"get_ds {self.config['MONGODB_SERVER']}")
        
        #if ds_name in self.config:

        if ds_name in self.data_source:
            db = self.data_source[ds_name]
            COL = self.config[col_name]
            return db[COL]
            

        if (hasattr(self.args, 'remote_db') and self.args.remote_db) or \
            ('remote_db' in self.args and self.args['remote_db']) or \
            self.config["REMOTE_DB"]:
            REMOTE_HOST = self.config["REMOTE_HOST"]
            REMOTE_PORT = self.config["REMOTE_PORT"]
            REMOTE_BINDING_ADDR = self.config["REMOTE_BINDING_ADDR"]
            REMOTE_BINDING_PORT = self.config["REMOTE_BINDING_PORT"]
            REMOTE_USER = self.config["REMOTE_USER"]
            REMOTE_PASS = self.config["REMOTE_PASS"]
            logger.debug(f"connect to remote db at {REMOTE_HOST} {REMOTE_PORT} {REMOTE_USER}")
            connection_key = REMOTE_HOST + f"{REMOTE_PORT}"
            if connection_key in self.connection:
                conn = self.connection[connection_key]["connection"]
            else:
                server = SSHTunnelForwarder(
                    (REMOTE_HOST, REMOTE_PORT),
                    ssh_username=REMOTE_USER,
                    ssh_password=REMOTE_PASS,
                    remote_bind_address=(REMOTE_BINDING_ADDR, REMOTE_BINDING_PORT)
                )
                server.start()
                conn = MongoClient(REMOTE_BINDING_ADDR, server.local_bind_port) # server.local_bind_port is assigned local port
                self.connection[connection_key] = {"connection":conn, "server":server}

        else:
            logger.debug(f"Connecting  to mongodb")
            MONGODB_SERVER = self.config["MONGODB_SERVER"]
            MONGODB_PORT = self.config["MONGODB_PORT"]
            logger.debug(f"connect to local db at {MONGODB_SERVER}  {MONGODB_PORT}")
            connection_key = MONGODB_SERVER + f"{MONGODB_PORT}"
            if connection_key in self.connection:
                conn = self.connection[connection_key]["connection"]
            else:
                logger.debug(f"Connecting  to {connection_key} first time.")
                conn = MongoClient(MONGODB_SERVER,MONGODB_PORT)
                self.connection[connection_key] = {"connection": conn}

        MONGODB_DBNAME = self.config["MONGODB_DBNAME"]
        db = conn[MONGODB_DBNAME]
        self.data_source[ds_name] = db
        dbstats = db.command("dbstats")
        logger.debug(f"{dbstats}")
        COL = self.config[col_name]
        #total_count = db[COL].count_documents({}) # cause long time to run
        logger.debug(f"connected data source: {MONGODB_DBNAME}[{COL}]")
        return db[COL]
        
        # dbcol.create_index([("host", pymongo.ASCENDING),("port", pymongo.ASCENDING) ], name='idx_host_port', unique = True)
        # dbcol.create_index([("verified", pymongo.ASCENDING), ("verified_time", pymongo.ASCENDING) ], name='idx_verified', unique = False)
        # logger.debug(db.list_collection_names())

    def __del__(self): 
        if(hasattr(self.args, 'remote_db') and self.args.remote_db and self.connection ):
            logger.debug(f"Shutdown remote server connection")
            for i, (conn_key, conn) in enumerate(self.connection.items()):
                if "server" in conn and conn["server"]:
                    conn["server"].stop()
                    logger.debug(f"{conn_key} server is stopped.")

def save_to_proxy_db(dbcol, proxylist):
    
    total = 0
    for proxy in proxylist:

        update_proxy_to_db(dbcol, proxy)
        total += 1
        
    logger.debug(f'Finsihed save_to_proxy_db with {total} records')

def update_proxy_to_db(dbcol, proxy):
    
    logger.debug(proxy)
    if("host" not in proxy):
        return
        
    if("port" not in proxy or not proxy["port"]):
        proxy["port"] = 80
    elif isinstance(proxy["port"], str):
        if not proxy["port"].isdigit():
            return
        else:
            proxy["port"] = int(proxy["port"])

    create_time = datetime.now()
    proxy["update_time"] = create_time
    dbcol.update(   {  "host": proxy["host"], "port": proxy["port"]},
                    {  "$setOnInsert": {"created_time": create_time}, 
                        "$set":proxy
                    },
                    upsert=True)

    logger.debug(f'new proxy {proxy["host"]}:{proxy["port"]}')
