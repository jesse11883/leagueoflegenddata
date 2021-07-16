import time, sys, os, copy, json, re, random, traceback
import requests
import urllib.parse
import shortuuid

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
    found = True
    new_match = {
        "count": match["count"]
        }
    puuid_bg = match["puuid_bg"]
    summoner =   get_db_summoner().find_one({"bobsprite1.puuid":puuid_bg})
    if (summoner):
        new_match["uid_bg"] = summoner["uid"]
    else:
        logger.debug(f"can not find {match} puuid_bg {puuid_bg}")
        return

    puuid_sm = match["puuid_sm"],
    summoner =   get_db_summoner().find_one({"bobsprite1.puuid":puuid_sm})
    if (summoner):
        new_match["uid_sm"] = summoner["uid"]
    else:
        logger.debug(f"can not find puuid_sm {puuid_sm}")
        return   

    if (new_match["uid_sm"] > new_match["uid_bg"]):
        a = new_match["uid_sm"]
        new_match["uid_sm"] = new_match["uid_bg"]
        new_match["uid_bg"] = a


    get_db_pat_con_count_unified().update_one({"uid_sm": new_match["uid_sm"],"uid_bg": new_match["uid_bg"]}, {"$set":new_match}, upsert = True)
    get_db_pat_con_count().update_one({"_id": match["_id"]}, {"$set":{"processed" : True}})

    return found

def main(args) -> None:
    commondb.initdb(args)
    match_count = 0
    wrong_count = 0
    while True:
        query = { "processed": {"$exists": False} }
        match_list = list(get_db_pat_con_count().find(query).limit(100))
        if (len(match_list) == 0):
            logger.debug("we are done")
            break
        
        for match in match_list:
            ret = process_one_match(match)
            if (not ret):
                wrong_count+= 1
            match_count += 1
            if (match_count % 1000 == 0):
                logger.debug(f"processing {match_count} now.")
                logger.debug(f"processing wrong {wrong_count} now.")
        



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