# -*- coding:utf-8 -*-
import logging
import sys

from bottle import run
import memcache
import redis

from LRUCache import LRUCache
from handlers import *

# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  #用户上传文件大小的上限
# cache = LRUCache() #use LRUCache
# cache = memcache.Client(['127.0.0.1:11211'], debug = 1)


def setup_logging():
    FORMAT = "%(asctime)s %(levelname)s %(process)d %(message)s"
    formatter = logging.Formatter(FORMAT)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)


if __name__ == '__main__':
    setup_logging()
    cache = redis.StrictRedis(host='127.0.0.1', port=6379, db=1)
    run(host='localhost', port=5000, reloader=True)
