# -*- coding:utf-8 -*-
from collections import OrderedDict

class LRUCache(object):
def __init__(self, capacity):
    self.capacity = capacity
    self.cache = OrderedDict()

def set(self, key, value):
    try:
        self.cache.pop(key)
    except KeyError:
        if len(self.cache) >= self.capacity:
            self.cache.popitem(last=False)
    self.cache[key] = value

def get(self, key):
    try:
        value = self.cache.pop(key)
        self.cache[key] = value
        return value
    except KeyError:
        return -1


