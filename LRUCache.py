# -*- coding:utf-8 -*-
from collections import OrderedDict

class LRUCache(object):

def __init__(self, capacity):
    self.__capacity = capacity
    self.__cache = OrderedDict()

def set(self, key, value):
    try:
        self.__cache.pop(key)
    except KeyError:
        if len(self.cache) >= self.__capacity:
            self.__cache.popitem(last=False)
    self.__cache[key] = value

def get(self, key):
    try:
        value = self.__cache.pop(key)
        self.__cache[key] = value
        return value
    except KeyError:
        return -1

def clear(self):
    self.__cache.clear()



