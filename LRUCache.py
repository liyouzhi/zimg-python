# -*- coding:utf-8 -*-
import time

from collections import OrderedDict


# logging
class LRUCache(object):
    def __init__(self, capacity=1024, TTL=24 * 60 * 60):
        self.capacity = capacity
        self.TTL = TTL

        self.__cache = OrderedDict()
        self.__expiration_time = {}

    def set(self, key, value):
        if key in self.__cache:
            self.__delete(key)
        else:
            if len(self.__cache) >= self.capacity:
                k, v = self.__cache.popitem(last=False)
                del self.__expiration_time[k]
        self.__cache[key] = value
        t = int(time.time())
        self.__expiration_time[key] = t + self.TTL
        print('set cache:', key)

    def get(self, key):
        if key in self.__cache:
            value = self.__cache.pop(key)
            self.__cache[key] = value
            print('get cache: %s len: %s' % (key, len(value)))
            return value
        else:
            return None

    def clear(self):
        self.__cache.clear()
        self.__expiration_time.clear()

    def __delete(self, key):
        del self.__cache[key]
        del self.__expiration_time[key]


def test():
    cache = LRUCache()
    k = 'foo'
    v = 'bar'
    cache.set(k, v)
    vv = cache.get(k)
    if vv != v:
        print('value mismatch!', vv)
    else:
        print('pass')


if __name__ == '__main__':
    test()
