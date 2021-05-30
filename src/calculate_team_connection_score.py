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
db_pat_match = None
db_pat_con_count = None
db_game_connection_impact = None

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

def get_db_pat_con_count():
    global db_pat_con_count
    return db_pat_con_count

def get_db_game_connection_impact():
    global db_game_connection_impact
    return db_game_connection_impact

def print_pretty(obj):
  logger.debug(json.dumps(obj, indent=2,ensure_ascii=False))


#team can only be 0 or 1
def process_one_match(md, team):
    if ("metadata" not in md):
        logger.debug(md)
        return
    
    pats = md["metadata"]["participants"]
    if (len(pats) < 10):
        logger.debug(f"invalid size of pats {len(pats)} in match {md['matchid']}, corrupted data?")
        return
    dobj = {}
    bounding_scores = []
    for i in range(4):
        for j in range(i+1,5):
            logger.debug(f"{i}  {j} {i + team*5} {len(pats)}  {i + team*5}")
            puuid_sm = pats[i + team*5] 
            puuid_bg= pats[j + team*5]
            if (puuid_sm > puuid_bg):
                p = puuid_sm
                puuid_sm = puuid_bg
                puuid_bg = p
            pair_score = get_db_pat_con_count().find_one({"puuid_sm": puuid_sm, "puuid_bg":puuid_bg})
            if pair_score == None:
                logger.debug(f"Can not find pair_score for {puuid_sm} {puuid_bg} in match {md['matchid']}")
                return
            dobj[f"{i}_{j}"] = pair_score["count"]
            bounding_scores.append(pair_score["count"])

    bounding_scores.sort(reverse=True)
    total_connection_score = 0
    for t in range(len(bounding_scores)):
        dobj[f"cs_{t:02d}"] = bounding_scores[t]
        total_connection_score += bounding_scores[t]
    dobj["total_cs"] = total_connection_score
    dobj["gameDuration"] = md["info"]["gameDuration"]
    dobj["matchid"] = md["matchid"]
    total_kills = 0
    total_death = 0

    for k in range(5):
        pat = md["info"]["participants"][k+team*5]
        total_death += pat["deaths"]
        total_kills += pat["kills"]
    dobj["total_death"] = total_death
    dobj["total_kills"] = total_kills

    total_obj = len(md["info"]["teams"][team]["objectives"])
    win = md["info"]["teams"][team]["win"]
    dobj["total_obj"] = total_obj
    dobj["win"] = win
    get_db_game_connection_impact().update_one({"matchid":dobj["matchid"], "teamid": team }, {"$set":dobj}, upsert=True)
    logger.debug(f"updateed {md['matchid']}")


def main(args) -> None:
    global dbconn
    global db_summoner
    global db_match_list
    global db_match_detail
    global db_match_timeline
    global db_team_stats
    global db_pat_match
    global db_pat_con_count
    global db_game_connection_impact

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
    db_pat_con_count = dbconn.get_ds("MONGODB_DBNAME", "PAT_CONNECTION_COUNT_COLLECTION")
    #we use puuid_sm and puuid_bg pair to conunt number of connect of these two keys. puuid_sm should ALWAYS smaller than puuid_bg
    db_pat_con_count.create_index([("puuid_sm", pymongo.ASCENDING), ("puuid_bg", pymongo.ASCENDING)], name='idx_conn_idx', unique = True)
    
    db_game_connection_impact = dbconn.get_ds("MONGODB_DBNAME", "GAME_CONNECTION_IMPACT_COLLECTION")
    #we use puuid_sm and puuid_bg pair to conunt number of connect of these two keys. puuid_sm should ALWAYS smaller than puuid_bg
    db_game_connection_impact.create_index([("matchid", pymongo.ASCENDING), ("teamid", pymongo.ASCENDING)], name='idx_matchid_teamid', unique = True)
    
    match_detail_list = db_match_detail.find({}).sort("_id",pymongo.ASCENDING)
    match_count = 0
    for m in match_detail_list:
        process_one_match(m, 0)
        process_one_match(m, 1)
        match_count += 1
        if (match_count % 1000 == 0):
            logger.debug(f"processing {match_count} now. {m['matchid']}")
    



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