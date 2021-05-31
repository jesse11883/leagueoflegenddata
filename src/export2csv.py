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
from bson.json_util import loads

from datetime import datetime, timedelta, timezone
import pytz
import logging

from pprint import pprint, pformat, PrettyPrinter 
import argparse
from pathlib import Path
import time
import csv
import x8common
from commondb import *
import commondb

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


def print_pretty(obj):
  logger.debug(json.dumps(obj, indent=2,ensure_ascii=False))



def main(args) -> None:
    commondb.initdb(args)
    with open('game_connection_impact.csv', mode='w') as csv_file:
        fieldnames = [ 'matchid', 'teamid',  
            '0_1', '0_2',  '0_3','0_4',  '1_2' ,'1_3', '1_4',  '2_3','2_4', '3_4',
            'cs_00','cs_01',  'cs_02','cs_03','cs_04', 'cs_05', 'cs_06', 'cs_07', 'cs_08', 'cs_09',  
            'total_cs', 'gameDuration',  'win',  'total_death', 'total_kills',  'total_obj']
          
         
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        match_detail_list = get_db_game_connection_impact().find({}, {"_id":0}).sort("_id",pymongo.ASCENDING)
        match_count = 0
        for m in match_detail_list:
            logger.debug(f"{m['matchid']}")
            output = loads(dumps(m))
            writer.writerow(output)


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