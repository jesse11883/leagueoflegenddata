import time, sys, os, copy, json, re, random, traceback
import requests
import urllib.parse

from ratelimit import limits, sleep_and_retry
from pymongo import MongoClient
import pymongo
from bson.objectid import ObjectId
from bson.json_util import dumps


from dbconn import DBConnection
from config import DevelopmentConfig
import x8common

dbconn = None 
db_summoner = None
db_match_list = None
db_match_detail = None
db_match_timeline = None 
db_team_stats = None
db_pat_match = None
db_pat_match_unified = None
db_pat_con_count = None
db_pat_con_count_unified = None
db_game_connection_impact = None
db_match_team_unified = None 
db_developers = None 

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

def get_db_pat_match():
    global db_pat_match
    return db_pat_match

def get_db_pat_match_unified():
    global db_pat_match_unified
    return db_pat_match_unified

def get_db_pat_con_count():
    global db_pat_con_count
    return db_pat_con_count

def get_db_pat_con_count_unified():
    global db_pat_con_count_unified
    return db_pat_con_count_unified

def get_db_game_connection_impact():
    global db_game_connection_impact
    return db_game_connection_impact

def get_db_match_team_unified():
    global db_match_team_unified
    return db_match_team_unified

def get_db_developers():
    global db_developers
    return db_developers

def initdb(args):
    global dbconn
    global db_summoner
    global db_match_list
    global db_match_detail
    global db_match_timeline
    global db_team_stats
    global db_pat_match
    global db_pat_con_count
    global db_pat_con_count_unified
    global db_game_connection_impact
    global db_match_team_unified
    global db_pat_match_unified
    global db_developers
    
    cfg = DevelopmentConfig()
    dbconn = DBConnection(args, cfg)

    db_summoner = dbconn.get_ds("MONGODB_DBNAME", "SUMMONER_COLLECTION")
    
    db_summoner.create_index([("name", pymongo.ASCENDING)], name='idx_name', unique = True)
    db_summoner.create_index([("uid", pymongo.ASCENDING)], name='idx_uid', unique = True)
    db_summoner.create_index([("bobsprite1.puuid", pymongo.ASCENDING)], name='idx_bob_puuid', unique = False)
    db_match_list = dbconn.get_ds("MONGODB_DBNAME", "MATCH_LIST_COLLECTION")
    db_match_list.create_index([("puuid", pymongo.ASCENDING),("matchid", pymongo.ASCENDING)], name='idx_puuid_matchid', unique = True)
    db_match_detail = dbconn.get_ds("MONGODB_DBNAME", "MATCH_DETAIL_COLLECTION")
    db_match_detail.create_index([("matchid", pymongo.ASCENDING)], name='idx_matchid', unique = True)
    db_match_timeline = dbconn.get_ds("MONGODB_DBNAME", "MATCH_TIMELINE_COLLECTION")
    db_match_timeline.create_index([("matchid", pymongo.ASCENDING)], name='idx_matchid', unique = True)
    db_pat_match = dbconn.get_ds("MONGODB_DBNAME", "PAT_MATCH_COLLECTION")
    db_pat_match.create_index([("puuid", pymongo.ASCENDING), ("matchid", pymongo.ASCENDING),("teamid", pymongo.ASCENDING)], name='idx_pat_match_team', unique = True)
    db_pat_match.create_index([("puuid", pymongo.ASCENDING)], name='idx_pat', unique = False)

    db_pat_match_unified = dbconn.get_ds("MONGODB_DBNAME", "PAT_MATCH_UNIFIED_COLLECTION")
    db_pat_match_unified.create_index([("uid", pymongo.ASCENDING), ("matchid", pymongo.ASCENDING),("teamid", pymongo.ASCENDING)], name='idx_pat_match_team', unique = True)
    db_pat_match_unified.create_index([("uid", pymongo.ASCENDING)], name='idx_pat', unique = False)



    #db_pat_match.create_index([("processid", pymongo.ASCENDING)], name='idx_processed', unique = True)
    db_pat_con_count = dbconn.get_ds("MONGODB_DBNAME", "PAT_CONNECTION_COUNT_COLLECTION")
    #we use puuid_sm and puuid_bg pair to conunt number of connect of these two keys. puuid_sm should ALWAYS smaller than puuid_bg
    db_pat_con_count.create_index([("puuid_sm", pymongo.ASCENDING), ("puuid_bg", pymongo.ASCENDING)], name='idx_conn_idx', unique = True)
    
    #db_pat_match.create_index([("processid", pymongo.ASCENDING)], name='idx_processed', unique = True)
    db_pat_con_count_unified = dbconn.get_ds("MONGODB_DBNAME", "PAT_CONNECTION_COUNT_UNIFIED_COLLECTION")
    #we use puuid_sm and puuid_bg pair to conunt number of connect of these two keys. puuid_sm should ALWAYS smaller than puuid_bg
    db_pat_con_count_unified.create_index([("uid_sm", pymongo.ASCENDING), ("uid_bg", pymongo.ASCENDING)], name='idx_conn_idx', unique = True)

    db_game_connection_impact = dbconn.get_ds("MONGODB_DBNAME", "GAME_CONNECTION_IMPACT_COLLECTION")
    #we use puuid_sm and puuid_bg pair to conunt number of connect of these two keys. puuid_sm should ALWAYS smaller than puuid_bg
    db_game_connection_impact.create_index([("matchid", pymongo.ASCENDING), ("teamid", pymongo.ASCENDING)], name='idx_matchid_teamid', unique = True)
    

    db_match_team_unified = dbconn.get_ds("MONGODB_DBNAME", "MATCH_TEAM_COLLECTION")
    #we use puuid_sm and puuid_bg pair to conunt number of connect of these two keys. puuid_sm should ALWAYS smaller than puuid_bg
    db_match_team_unified.create_index([("matchid", pymongo.ASCENDING)], name='idx_matchid', unique = True)
    
    db_developers = dbconn.get_ds("MONGODB_DBNAME", "DEVELOPERS_COLLECTION")
    
    db_developers.create_index([("uid", pymongo.ASCENDING)], name='idx_uid', unique = True)
    db_developers.create_index([("login", pymongo.ASCENDING)], name='idx_login', unique = True)
    
