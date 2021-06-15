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
    pair_count = 0
    missing_puuid = []
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
                missing_puuid.append(puuid_sm)
                missing_puuid.append(puuid_bg)
                pair_count += 1
            else:
                dobj[f"{i}_{j}"] = pair_score["count"]
                bounding_scores.append(pair_score["count"])

    logger.debug(f"pair_count {pair_count} {len(missing_puuid)}")
    if (pair_count == 0):
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
        
        logger.debug(f"updateed {md['matchid']}")
        return dobj
    else:
        unique_puuid = list(set(missing_puuid))
        if (len(unique_puuid)) == 2:
            for un in unique_puuid:
                logger.debug(f"will updateed unique_puuid {un}")
                get_db_summoner().update( { "puuid":un }, {"$set":{"needUpdate":True}})
        else:
            logger.debug(f"not updateed unique_puuid {len(unique_puuid)}")
            return

def main(args) -> None:
    commondb.initdb(args)

    match_detail_list = get_db_match_detail().find({}).sort("_id",pymongo.ASCENDING)
    match_count = 0
    for m in match_detail_list:
        db_team0 = process_one_match(m, 0)
        db_team1 = process_one_match(m, 1)
        if (not db_team0 or not db_team1):
            continue
        db_team0["delta_cs"] = db_team0["total_cs"] - db_team1["total_cs"]
        db_team1["delta_cs"] = db_team1["total_cs"] - db_team0["total_cs"]
        get_db_game_connection_impact().update_one({"matchid":db_team0["matchid"], "teamid": 0 }, {"$set":db_team0}, upsert=True)
        get_db_game_connection_impact().update_one({"matchid":db_team1["matchid"], "teamid": 1 }, {"$set":db_team1}, upsert=True)
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