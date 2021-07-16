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
from commondb import *
import commondb
from commonapi import *

def print_pretty(obj):
  logger.debug(json.dumps(obj, indent=2,ensure_ascii=False))

def process_one_match(match):
    teams = []
    if "info" not in match:
        logger.debug(f'{match["_id"]} has not data')
        s = datetime.now()
        get_db_match_detail().update_one({"_id": match["_id"]}, {"$set":{"unified" : True, "wrongdata": True}})
        e = datetime.now()
        calculate_perf("match_detail.update_one", e-s)
        return False

    for pat in match["info"]["participants"]:
        if "user_id" not in pat and "uid" not in pat and "puuid" not in pat:
            logger.debug(f'{match["_id"]} has no data')
            s = datetime.now()
            get_db_match_detail().update_one({"_id": match["_id"]}, {"$set":{"unified" : True, "wrongdata": True}})
            e = datetime.now()
            calculate_perf("match_detail.update_one", e-s)
            return False
        if "puuid" in pat and pat["puuid"] == "BOT":
            teams.append("BOT")
            continue
        #logger.debug(f"{match['matchid']}  {pat['summonerName']}")
        if "uid" in pat:
            teams.append(pat["uid"])
            continue
        summoner = None
        if 'puuid' in pat:
            s = datetime.now()
            summoner =   list(get_db_summoner().find({"bobsprite1.puuid":pat["puuid"]}))
            e = datetime.now()
            calculate_perf("get_db_summoner().find", e-s)
        else:
            s = datetime.now()
            summoner =   list(get_db_summoner().find({"_id":pat["user_id"]}))
            e = datetime.now()
            calculate_perf("get_db_summoner().find", e-s)
        if len(summoner) == 1:
            pat["uid"] = summoner[0]["uid"]
            teams.append(pat["uid"])
            if("user_id" in pat):
                del pat["user_id"]
            if("puuid" in pat):
                del pat["puuid"]
        else:
            logger.debug(f'{match["_id"]} has not data')
            s = datetime.now()
            get_db_match_detail().update_one({"_id": match["_id"]}, {"$set":{"unified" : True, "wrongdata": True}})
            e = datetime.now()
            calculate_perf("match_detail.update_one", e-s)
            return False
    else:
        match["metadata"]["participants"] = teams
        match["unified"] = True
        s = datetime.now()
        get_db_match_detail().update_one( {"_id": match["_id"]}, {"$set":match}, upsert=True)
        e = datetime.now()
        calculate_perf("match_detail.update_one_big", e-s)
        return True
    
    # get_db_match_detail().update_one({"matchid": match["matchid"]}, {"$set":{"unified" : True}})

performance_count = {}

def calculate_perf(name, timespend):
    global performance_count
    perf = {"count":0, "p": timedelta(0), "ave": timedelta(0)}
    if (name in performance_count):
        perf = performance_count[name]
    else:
        performance_count[name] = perf
    
    perf["count"] += 1
    perf["p"] += timespend
    perf["ave"] = perf["p"] / perf["count"]

def main(args) -> None:
    commondb.initdb(args)
    match_count = 0
    wrong_count = 0
    while True:
        query = { "unified": {"$ne" : True} }
        s = datetime.now()
        match_list = list(get_db_match_detail().find(query).limit(100))
        e = datetime.now()
        calculate_perf("match_detail.find", e-s)
        if (len(match_list) == 0):
            logger.debug("we are done")
            break

        for match in match_list:
            s = datetime.now()
            result = process_one_match(match)
            e = datetime.now()
            calculate_perf("process_one_match", e-s)
            if (not result):
                wrong_count+= 1
            match_count += 1
            if (match_count % 500 == 0):
                logger.debug(f"processing {match_count} now. {wrong_count} wrong matches")
                print_pretty(json.loads(json.dumps(performance_count, indent=4, sort_keys=True, default=str)))


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