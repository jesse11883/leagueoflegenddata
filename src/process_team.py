import time, sys, os, copy, json, re, random, traceback
import requests
import urllib.parse

from ratelimit import limits, sleep_and_retry

from random import shuffle
import urllib3, requests
from pymongo import MongoClient
import pymongo
from bson.objectid import ObjectId
from bson.json_util import dumps
from datetime import datetime, timedelta, timezone
import pytz
import logging

from pprint import pprint, pformat, PrettyPrinter 
import argparse
from pathlib import Path
import time
timestring = time.strftime("_%Y_%m_%d_%H_%M_%S")
logger = logging.getLogger("loldata")
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler("./logs/loldata" + timestring +  '.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
# add the handlers to logger
logger.addHandler(ch)
logger.addHandler(fh)


pp = PrettyPrinter(indent=4)

from dbconn import DBConnection
from config import DevelopmentConfig
import x8common

dbconn = None 
db_summoner = None
db_match_list = None
db_match_detail = None
db_match_timeline = None 
db_team_stats = None

def get_dbconn():
    global dbconn
    return dbconn

def get_db_summoner():
    global db_summoner
    return db_summoner

def get_db_match_list():
    global db_match_list
    return db_match_list

def get_db_match_detail():
    global db_match_detail
    return db_match_detail

def get_db_match_timeline():
    global db_match_timeline
    return db_match_timeline

def get_db_pat_match():
    global db_pat_match
    return db_pat_match



def print_pretty(obj):
  logger.debug(json.dumps(obj, indent=2,ensure_ascii=False))





def main(args) -> None:
    global dbconn
    global db_summoner
    global db_match_list
    global db_match_detail
    global db_match_timeline
    global db_team_stats

    cfg = DevelopmentConfig()
    dbconn = DBConnection(args, cfg)

    db_summoner = dbconn.get_ds("MONGODB_DBNAME", "SUMMONER_COLLECTION")
    db_summoner.create_index([("puuid", pymongo.ASCENDING)], name='idx_puuid', unique = True)
    db_summoner.create_index([("name", pymongo.ASCENDING)], name='idx_name', unique = False)
    db_summoner.create_index([("accountId", pymongo.ASCENDING)], name='idx_accountId', unique = False)
    db_match_list = dbconn.get_ds("MONGODB_DBNAME", "MATCH_LIST_COLLECTION")
    db_match_list.create_index([("puuid", pymongo.ASCENDING),("matchid", pymongo.ASCENDING)], name='idx_puuid_matchid', unique = True)
    db_match_detail = dbconn.get_ds("MONGODB_DBNAME", "MATCH_DETAIL_COLLECTION")
    db_match_detail.create_index([("matchid", pymongo.ASCENDING)], name='idx_matchid', unique = True)
    db_match_timeline = dbconn.get_ds("MONGODB_DBNAME", "MATCH_TIMELINE_COLLECTION")
    db_match_timeline.create_index([("matchid", pymongo.ASCENDING)], name='idx_matchid', unique = True)
    db_pat_match = dbconn.get_ds("MONGODB_DBNAME", "PAT_MATCH_COLLECTION")
    db_pat_match.create_index([("puuid", pymongo.ASCENDING), ("matchid", pymongo.ASCENDING),("teamid", pymongo.ASCENDING)], name='idx_pat_match_team', unique = True)
    db_pat_match.create_index([("puuid", pymongo.ASCENDING)], name='idx_pat', unique = False)
    #db_pat_match.create_index([("processid", pymongo.ASCENDING)], name='idx_processed', unique = True)

    max_processid = db_pat_match.find().sort("processid",pymongo.DESCENDING).limit(1)
    for p in max_processid:
        print(p)
    match_list = db_match_detail.find({"info.queueId":400}).sort("_id",pymongo.DESCENDING)
    count = 0
    #total = db_match_detail.count_documents({"_id" :{"$gte": max_processid}, "info.queueId":400})
    #logger.debug(f"query matchid {total}")
    for match in match_list:
        for pat in match["info"]["participants"]:
            pat_match = {   "puuid": pat["puuid"], 
                            "summonerName": pat["summonerName"],
                            "teamid": pat["teamId"],
                            "matchid": match["matchid"]
                        }
            print(pat_match)
            db_pat_match.update_one(
                {"puuid": pat["puuid"],"teamid": pat["teamId"], "matchid": match["matchid"] },
                {"$set": {"summonerName": pat["summonerName"], "processid": match["_id"]}},
                upsert=True)
            count += 1
            if( count % 1000 ):
                logger.debug(f'update:{count} -> {pat["summonerName"]} {match["matchid"]} ')




def add_extra_arg(parser):
    parser.add_argument('--cmd', action='store',
                dest='cmd', default='getdata',
                help='command to run')    

    parser.add_argument("-imgpath", '--images_path', action='store',
                dest='images_path', 
                help='images path to upload')

    #https://stackoverflow.com/questions/15753701/how-can-i-pass-a-list-as-a-command-line-argument-with-argparse
    parser.add_argument('--subcmds', nargs='*', action='store',
                dest ='subcmds')
       
if __name__ == "__main__":

    args = x8common.init_argparse(add_extra_arg)

    logger.info(f"cmd:{args.cmd}")

    main(args)