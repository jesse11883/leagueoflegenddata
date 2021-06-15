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

pp = PrettyPrinter(indent=4)

from dbconn import DBConnection
from config import DevelopmentConfig
import x8common
from commondb import *
import commondb

logger = logging.getLogger("loldata")

summonerName = "bobsprite1"
URL_AM = "https://americas.api.riotgames.com"
URL_NA = "https://na1.api.riotgames.com"
TWO_MINUTES = 10


def print_pretty(obj):
  logger.debug(json.dumps(obj, indent=2,ensure_ascii=False))

@sleep_and_retry
@limits(calls=8, period=TWO_MINUTES)
def retrieve(url, base_url = URL_NA):
    headers ={ "X-Riot-Token":'RGAPI-b36581ec-34ec-4d43-9d39-639705308c25'}
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