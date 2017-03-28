# -*- coding:utf-8 -*-
import logging
import sys

from bottle import run, route, Bottle
# import memcache
# import redis

# from LRUCache import LRUCache
from handlers import home, post_image, multipart_post_image, get_image

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


setup_logging()
app = Bottle()
# cache = redis.StrictRedis(host='127.0.0.1', port=6379, db=1)

app.route('/', 'GET', home)
app.route('/images', 'POST', post_image)
app.route('/images/multipart', 'POST', multipart_post_image)
app.route('/images/<image_id>', 'GET', get_image)

if __name__ == '__main__':
    app.run(host='localhost', port=5000, reloader=True)
