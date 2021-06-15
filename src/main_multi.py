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

summonerName = "bobsprite1"
URL_AM = "https://americas.api.riotgames.com"
URL_NA = "https://na1.api.riotgames.com"
TWO_MINUTES = 10

dbconn = None 
db_summoner = None
db_match_list = None
db_match_detail = None
db_match_timeline = None 

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



def print_pretty(obj):
  logger.debug(json.dumps(obj, indent=2,ensure_ascii=False))

@sleep_and_retry
@limits(calls=8, period=TWO_MINUTES)
def retrieve(url, base_url = URL_NA):
    headers ={ "X-Riot-Token":'RGAPI-2b492c13-410f-4f0e-8abb-f4bd1d92d32e'}
    request_url = urllib.parse.urljoin(base_url, url)
    r = requests.get(request_url,  headers=headers)
    return r.json()

def get_summoner_by_name(summoner_name):
    r = retrieve(f"/lol/summoner/v4/summoners/by-name/{summoner_name}")
    return r

def get_match_list_puuid(puuid):
    base_url = URL_AM
    start = 0
    count = 100
    match_list = []
    while True:
        r = retrieve(f"/lol/match/v5/matches/by-puuid/{puuid}/ids?start={start}&count={count}", base_url)
        logger.debug(json.dumps(r, indent=2,ensure_ascii=False))
        try:
            match_list = match_list + r
        except:
            logger.error(json.dumps(r, indent=2,ensure_ascii=False))
            raise
        if (len(r) < count):
            break
        else:
            start = start + count
    return match_list

def get_match_timeline(matchId):
    r = retrieve(f"/lol/match/v5/matches/{matchId}/timeline", URL_AM)
    return r

def get_match_detail(matchId):
    r = retrieve(f"/lol/match/v5/matches/{matchId}", URL_AM)
    return r   

def get_summoner_by_puuid(puuid):
    r = retrieve(f"/lol/summoner/v4/summoners/by-puuid/{puuid}")
    logger.debug(f"r=>{r}")
    return r

def fetch_one_puuid(puuid):
    logger.info(f"process puuid {puuid}")
    r = get_summoner_by_puuid(puuid)
    logger.info(f"get summoner name: {r['name']}")
    get_db_summoner().update_one({"puuid":r["puuid"]}, {"$set":r}, upsert=True)
    m = get_match_list_puuid(r["puuid"])
    logger.info(f"get {len(m)} matches.")
    mcount = 0
    for matchid in m:
        logger.debug(f"query matchid {matchid}")
        matchobj = {"matchid":matchid}
        match_db_id = get_db_match_list().find_one({"matchid":matchid})
        update_detail = False
        update_timeline = False
        if (not match_db_id):

            logger.debug(f"add new match id:")
            logger.debug(json.dumps(matchobj, indent=2,ensure_ascii=False))
            get_db_match_list().update_one(matchobj, {"$set":matchobj}, upsert=True)
            update_detail = True
            update_timeline = True
        else:
            logger.debug(f"We had this match before {matchid}")
            match_detail_db = get_db_match_detail().find_one({"matchid":matchid},  {"metadata":1,"_id": False})
            if(not match_detail_db or (not match_detail_db["metadata"])):
                logger.debug(f"We are missing match detail for {matchid}")
                update_detail = True
                
            # match_timeline_db = get_db_match_timeline().find_one({"matchid":matchid},  {"metadata":1,"_id": False})
            # if(not match_timeline_db or (not match_timeline_db["metadata"])):
            #     logger.debug(f"We are missing match timeline for {matchid}")
            #     update_timeline = True

        if update_detail:
            match = get_match_detail(matchid)
            if  hasattr(match, "metadata") or "metadata" in match:
                logger.debug(f"update new match detail id: {matchid}")
                get_db_match_detail().update_one({"matchid":matchid}, {"$set":match}, upsert=True)
                #match = get_match_detail(matchid)
                #logger.debug(json.dumps(match, indent=2,ensure_ascii=False))
                logger.debug(json.dumps(match["metadata"]["participants"], indent=2,ensure_ascii=False))
                puuid_list = match["metadata"]["participants"]
                for pid in puuid_list:
                    get_db_summoner().update_one({"puuid":pid}, {"$set": {"puuid":pid}}, upsert=True)
            else:
                logger.error(f"fail to retrieve match detail id: {matchid}")
                logger.error(json.dumps(match, indent=2,ensure_ascii=False))
        mcount+=1
        if(mcount % 100 == 0):
            logger.info(f"processed {mcount}")
        # if update_timeline:
        #     match = get_match_timeline(matchid)
        #     if hasattr(match, "metadata") or "metadata" in match:
        #         logger.debug(f"update new match time id: {matchid}")
        #         get_db_match_timeline().update_one({"matchid":matchid}, {"$set":match}, upsert=True)
        #         #match = get_match_detail(matchid)
        #         #logger.debug(json.dumps(match, indent=2,ensure_ascii=False))
        #         logger.debug(json.dumps(match["metadata"]["participants"], indent=2,ensure_ascii=False))
        #         puuid_list = match["metadata"]["participants"]
        #         for pid in puuid_list:
        #             get_db_summoner().update_one({"puuid":pid}, {"$set": {"puuid":pid}}, upsert=True)
        #     else:
        #         logger.error(f"fail to retrieve match timeline id: {matchid}")
        #         logger.error(json.dumps(match, indent=2,ensure_ascii=False))




def main(args) -> None:
    global dbconn
    global db_summoner
    global db_match_list
    global db_match_detail
    global db_match_timeline
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


    r = get_summoner_by_name('bobsprite1')
    logger.debug(f"get_summoner_by_name {r}")
    puuid = r["puuid"]
    r = get_summoner_by_puuid(puuid)
    logger.debug(f"get_summoner_by_puuid {r}")
    m = get_match_list_puuid(r["puuid"])
    mcount = 0
    ## for matchid in m:
        #logger.debug(f"query matchid {matchid}")
        # matchobj = {"matchid":matchid}
        # logger.debug(f"matchobj {matchobj}")
    match = get_match_detail("NA1_3704345286")
    logger.debug(f"match detail {pformat(match)}")

    # count = 0
    # while True:
    #     pid_list = list(db_summoner.find({"name": {"$exists": False}, "needUpdate":True}, {"puuid":1,"_id": False}).sort("_id",pymongo.ASCENDING).limit(100))
    #     # pid_list = list(db_summoner.find({"name": {"$exists": False}}, {"puuid":1,"_id": False}).sort("_id",pymongo.ASCENDING).limit(100))
    #     if len(pid_list) == 0:
    #         logger.debug("We get all the puuid")
    #         break
    #     for puid in pid_list:
            
    #         fetch_one_puuid(puid["puuid"])
    #         get_db_summoner().update_one({"puuid":puid["puuid"]}, {"$set": {"needUpdate":False}}, upsert=False)
    #         count += 1
    #         if(count % 100 == 0):
    #             logger.info(f"processing {count} users")


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