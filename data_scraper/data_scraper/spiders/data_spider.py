# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import logging
from os import listdir
from os.path import isfile, join
import pathlib
import re
import os
import urllib.parse as urlparse
import string
import time
import json
import cProfile
from timeit import default_timer as timer
from pymongo import MongoClient
import pymongo
from bson.objectid import ObjectId
from bson.json_util import dumps

from dbconn import DBConnection
from config import DevelopmentConfig
import x8common
from commondb import *
import commondb


timestring = time.strftime("_%Y_%m_%d_%H_%M_%S")

#logging.basicConfig(filename='logs/chinavitaelocal' + timestring +  '.log', filemode='w', format="%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s", datefmt='%d-%b-%y %H:%M:%S', level=logging.DEBUG)
logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# # create formatter and add it to the handlers
formatter = logging.Formatter("%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s")
ch.setFormatter(formatter)
# # add the handlers to the logger
logger.addHandler(ch)

file_handler = logging.FileHandler('logs/dataspider' + timestring +  '.log')
formatter    = logging.Formatter("%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s")
file_handler.setFormatter(formatter)
# add file handler to logger
logger.addHandler(file_handler)

# from scrapy.utils.project import get_project_settings

# settings=get_project_settings()



class DataSpider(scrapy.Spider):
    name = "loldata"

    def get_data(self):
        query = {"$and":[]}
        query["$and"].append({{"revisionDate":{"$exists":True}}})
        query["$and"].append({{"fullset":{"$exists":False}}})
        summoners = list(get_db_summoner().find(query))
        return summoners

    def get_all_developers(self):
        self.developers = list(get_db_developers().find({}))
        

    def start_requests(self):
        logger.debug(f"start_requests")
        self.get_all_developers()
        summmoner =  self.get_data()
        
        urls = [
            
        ]
        for idx, val in enumerate(summmoner):
            header = url_header(uid)
            url = get_match_list_puuid_url(puuid, start, count)
            matchdata = {"start": start, "count": count, "match_list": [] }
            yield scrapy.Request(url=url, headers=header, cb_kwargs={"data":matchdata}, callback=self.parse)


    def parse(self, response, data):
        matchdata = data.matchdata
        start = matchdata.start
        count = matchdata.count
        r = json.loads(response.body_as_unicode())
        if (len(jsonres) == matchdata.count):
            matchdata.match_list = matchdata.match_list + r
            matchdata.start = matchdata.start + count
            yield scrapy.Request(url=url, headers=header, cb_kwargs={"data":matchdata}, callback=self.parse)
        else:
            data = matchdata.match_list + r
            yield data