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


def print_pretty(obj):
  logger.debug(json.dumps(obj, indent=2,ensure_ascii=False))


def process_one_pat(puuid):
    matching_rec = get_db_pat_match().count_documents({"puuid":puuid})
    #logger.debug(f"{puuid} has {matching_rec} matches")
    # We only process puuid that larger than me
    match_list = get_db_pat_match().find({"puuid":puuid})

    count = 0
    friend={}
    for match in match_list:
        matchid = match["matchid"]
        oneMatch = get_db_match_detail().find_one({"matchid":matchid})
        #logger.debug(f"oneMatch {oneMatch}")
        for pat in oneMatch["info"]["participants"]:
            if (pat["teamId"] == match["teamid"] and pat["puuid"] > puuid):
                if (pat["puuid"] in friend):
                    friend[pat["puuid"]] = friend[pat["puuid"]] + 1
                else:
                    friend[pat["puuid"]] = 1
            
            count += 1
            if( count % 1000 == 0):
                logger.debug(f'prroccess {puuid}  {count} teammates ')
    
    for i, (k, v) in enumerate(friend.items()):
        #if (v > 1):
            get_db_pat_con_count().update_one({"puuid_sm":puuid, "puuid_bg": k }, {"$set": {"count": v}}, upsert = True )
    
    if(len(friend) > 0):
        logger.debug(f"updating {puuid} is done, total teammates: {len(friend)}")

def main(args) -> None:
    commondb.initdb(args)
    # having summoner name is to make sure we have ALL the friend for this player
    puuid_list = get_db_summoner().find({"name":{"$exists": True}}).sort("puuid",pymongo.ASCENDING)
    pat_count = 0
    for p in puuid_list:
        process_one_pat(p["puuid"])
        pat_count += 1
        if (pat_count % 1000 == 0):
            logger.debug(f"processing {pat_count} now. {p}")
    



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