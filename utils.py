import requests
import threading
import logging
import time
from loguru import logger
import hashlib
import pymongo
from pymongo import MongoClient
from datetime import datetime
import asyncio
import aiohttp
from lxml import etree

CONCURRENCY = 5
semaphore = asyncio.Semaphore(CONCURRENCY)


def start_log():
    logging.basicConfig(
        format="%(asctime)s | %(levelname)s     | - %(message)s", level=logging.INFO
    )


def get_header():
    Referer = ("https://moodyz.com/works/date",)
    cookie = "_gid=GA1.2.511776779.1692668446; _session=eyJpdiI6Imd3SGUrRFZNa2dyWmdJSFg2YnkzbGc9PSIsInZhbHVlIjoiRzROVWk5RGJCWmxLczBvSG56QUZGNVRiTGpQbjU0Z2x5ZVlWWnJTMitHYVFhMGZCcTh4c3NPbGR3cWhuUXBzbUhqRUVac3F0SU5YQVE4YXByRU9uRWxTaW95TjJvWUdlWUx1OWNzWGZ4MmZSRGg5VFNHZ3A4SUhHOWx6M3pLZjQiLCJtYWMiOiI5MTM3YzQwYTZiMmEwMTE2ZTQ4ZGRlN2RiMTZmMzZjOTVjOTk4YzNiNmE0ZDViZmQxNTZkMDdjMDI4ZTY5ZDBlIiwidGFnIjoiIn0%3D; _ga_WYX06RPCXW=GS1.1.1692755314.5.1.1692755315.59.0.0; _ga=GA1.2.70165307.1692668446; _gat_UA-5722240-4=1"
    return {
        "cookie": cookie,
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.203",
    }


def return_response(url, option="t"):
    response = requests.get(url=url, headers=get_header())
    response.encoding = response.apparent_encoding
    if option == "t":
        return response.text
    elif option == "b":
        return response.content


def more_thread(n, func, func_tuple):
    threads = []
    for _ in range(n):
        own_thread = threading.Thread(target=func, args=func_tuple)
        own_thread.start()
        threads.append(own_thread)
    for _ in threads:
        _.join()


def check_for_updates(data_base, collection):
    res = mongodb_option(data_base, collection)
    r1 = res.collection.find_one({}, {"datetime": 1})
    r2 = res.collection.find(
        {"datetime": {"$gte": r1["datetime"]}}, {"tid": 1, "datetime": 1}
    ).sort("datetime", pymongo.DESCENDING)
    old_data = [i for i in r2]
    print(old_data)
    for i in r2:
        print(i)


class mongodb_option:
    def __init__(self, data_base=None, collection=None):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client[data_base]
        if collection:
            self.collection = self.db[collection]

    def list_collections(self):
        return self.db.list_collection_names()

    def insert_one(self, data):
        self.collection.insert_one(data)
        return None

    def insert_many(self, data):
        self.collection.insert_many(data)
        return None

    def show_collection(self):
        collection_stats = self.db.command("collstats", self.collection.name)
        print("*" * 50)
        print(f"|{'ns': <20}|{collection_stats['ns']}")
        print(f"|{'count': <20}|{collection_stats['count']}")
        print(f"|{'size': <20}|{collection_stats['size']}")
        print(f"|{'storageSize': <20}|{collection_stats['storageSize']}")
        print(f"|{'totalIndexSize': <20}|{collection_stats['totalIndexSize']}")
        print("*" * 50)

    def find(self, dic):
        res = self.collection.find({}, dic)
        return res


class aioRequest:
    def __init__(self, asy_func=None):
        self.asy_func = asy_func

    async def main(self, data):
        con = aiohttp.TCPConnector(verify_ssl=False)
        async with aiohttp.ClientSession(trust_env=True) as session:
            tasks = [asyncio.create_task(self.asy_func(session, i)) for i in data]
            await asyncio.gather(*tasks)

    def start(self, data: list):
        # print(1)
        asyncio.run(self.main(data))
