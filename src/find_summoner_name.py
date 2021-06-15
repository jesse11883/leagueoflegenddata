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


#team can only be 0 or 1
def process_one_match(md):
    if ("metadata" not in md):
        logger.debug(md)
        return
    
    pats = md["info"]["participants"]
    for i in range(len(pats)):
        pat = pats[i]
        get_db_summoner().update_one(
            {"puuid": pat["puuid"], "name": {"$exists": False}}, 
            {
                "$set":
                    {
                        "summonerLevel":pat["summonerLevel"], 
                        "name":pat["summonerName"],
                        "bobsprite1":{"puuid":pat["puuid"], "summonerId":pat["summonerId"]
                    }
                }
            }
            )


    

def main(args) -> None:
    commondb.initdb(args)

    match_detail_list = get_db_match_detail().find({}).sort("_id",pymongo.ASCENDING)
    match_count = 0
    for m in match_detail_list:
        process_one_match(m)
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