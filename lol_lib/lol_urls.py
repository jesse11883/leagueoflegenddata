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
URL_AM = "https://americas.api.riotgames.com"
URL_NA = "https://na1.api.riotgames.com"

@time_cache(3600)
def url_header(uid):
    developer = get_db_login.findOne({"uid":uid})
    headers = { "X-Riot-Token": f"{developer.api-key}"}
    return headers

def get_match_list_puuid_url(puuid, start, count):
    return f"{URL_AM}/lol/match/v5/matches/by-puuid/{puuid}/ids?start={start}&count={count}"

