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
  print(json.dumps(obj, indent=2,ensure_ascii=False))

@sleep_and_retry
@limits(calls=8, period=TWO_MINUTES)
def retrieve(url, base_url = URL_NA):
    headers ={ "X-Riot-Token":'RGAPI-93fb270d-7925-4b2e-a4b2-2865c2c31d7e'}
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
        print_pretty(r)
        match_list = match_list + r
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
    return r

def fetch_one_puuid(puuid):
    r = get_summoner_by_puuid(puuid)

    get_db_summoner().update_one({"puuid":r["puuid"]}, {"$set":r}, upsert=True)
    m = get_match_list_puuid(r["puuid"])

    for matchid in m:
        matchobj = {"matchid":matchid}
        match_db_id = get_db_match_list().find_one({"matchid":matchid})
        if (not match_db_id):

            get_db_match_list().update_one(matchobj, {"$set":matchobj}, upsert=True)

            match = get_match_detail(matchid)
            get_db_match_detail().update_one({"matchid":matchid}, {"$set":match}, upsert=True)
            #match = get_match_detail(matchid)
            print_pretty(match)
            puuid_list = match["metadata"]["participants"]
            for pid in puuid_list:
                get_db_summoner().update_one({"puuid":pid}, {"$set": {"puuid":pid}}, upsert=True)
        else:
            print(f"We had this match before {matchid}")

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
    print_pretty(r)
    db_summoner.update_one({"puuid":r["puuid"]}, {"$set":r}, upsert=True)
    puuid = r["puuid"]
    fetch_one_puuid(puuid)
    while True:
        pid_list = db_summoner.find({"name": {"$exists": False}}, {"puuid":1,"_id": False})
        if (len(pid_list)) == 0:
            print("We get all the puuid")
            break
        for puid in pid_list:
            fetch_one_puuid(puid)



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