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


#team can only be 0 or 1
def process_one_sumoner(summ):

    su_name = summ["name"]
    sum_name_list = get_db_summoner().find({"name":su_name})
    puuid_list = []
    for sname in sum_name_list:
        puuid_list.append(sname["bobsprite1"]["puuid"])
    
    for puuid in puuid_list:
        r = get_summoner_by_puuid(puuid)
        get_db_summoner().update_one({"bobsprite1.puuid":puuid}, {"$set":r}, upsert=True)
    

def main(args) -> None:
    commondb.initdb(args)
    query_pipeline = [  
                {"$group" : { "_id": "$name", "count": { "$sum": 1 } } },
                {"$match": {"_id" :{ "$ne" : None } , "count" : {"$gt": 1} } }, 
                {"$project": {"name" : "$_id", "_id" : 0, "count":"$count"} }
    ]
    print_pretty(query_pipeline)
    summoner_list = get_db_summoner().aggregate(query_pipeline, allowDiskUse=True)
    match_count = 0
    for summ in summoner_list:
        process_one_sumoner(summ)
        match_count += 1
        if (match_count % 1000 == 0):
            logger.debug(f"processing {match_count} now. {summ['name']}")
    



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