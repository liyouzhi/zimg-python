# -*- coding:utf-8 -*-
from collections import OrderedDict
from time

class LRUCache(object):

    def __init__(self, capacity=1024, TTL=24*60*60):
        self.capacity = capacity
        self.TTL = TTL

        self.__cache = OrderedDict()
        self.__expiration_time = {}

    def set(self, key, value):
        try:
            self.__delete(key)
        except KeyError:
            if len(self.cache) >= self.__capacity:
                k, v = self.__cache.popitem(last=False)
                del self.__expiration_time[k]
        self.__cache[key] = value
        t = int(time.time())
        self.__expiration_time[key] = t + TTL 

    def get(self, key):
        try:
            value = self.__cache.pop(key)
            self.__cache[key] = value
            return value
        except KeyError:
            return -1 

    def clear(self):
        self.__cache.clear()
        self.__expiration_time.clear()

    def __delete(self, key):
        del self.__cache[key]
        del self.__expiration_time[key]


