# -*- coding:utf-8 -*-
import math
import logging

from PIL import Image, ImageDraw

# def resize_image(addr, width, height):
#     im = Image.open(addr)
#     w, h = im.size
#     if width == 0:
#         width = int(height * w / h)
#     if height == 0:
#         height = int(width * h / w)
#     out = im.resize((width, height))
#     # ret = io.BytesIO()
#     # out.save(ret, im.format)
#     # return ret.getvalue()
#     return out
#


def resize_image(im, width, height):
    w, h = im.size
    f = w / h
    if width == 0:
        width = math.floor(height * f)
        if width == 0: width = 1
    if height == 0:
        height = math.floor(width / f)
        if height == 0: height = 1
    return im.resize((width, height))


def fill(im, width, height):  #gravity: center
    w, h = im.size
    xf = w / h
    yf = width / height
    if yf == xf:
        return im.resize((width, height))
    if yf > xf:
        w = width
        h = math.floor(w / xf)
        image = im.resize((w, h))
        # print('resize:%s * %s' % (w,h))
        region = (0, (h - height) / 2, w, (h + height) / 2)
        # print(region)
    if yf < xf:
        h = height
        w = math.floor(h * xf)
        image = im.resize((w, h))
        # print('resize:%s * %s' % (w,h))
        region = ((w - width) / 2, 0, (w + width) / 2, h)
        # print(region)
    return image.crop(region)


def fit(im, width, height):
    w, h = im.size
    xf = w / h
    yf = width / height
    if yf == xf:
        w = width
        h = height
    if yf < xf:
        w = width
        h = math.floor(w / xf)
    if yf > xf:
        h = height
        w = math.floor(h * xf)
    return im.resize((w, h))


def crop_image(im, width, height):
    w, h = im.size
    region = ((w - width) / 2, (h - height) / 2, (w + width) / 2,
              (h + height) / 2)
    return im.crop(region)

# def transfer_format(im_data, im_format):
#     im = Image.open(io.BytesIO(im_data))
#     ret = io.BytesIO()
#     im.save(ret, im_format)
#     return ret.getvalue()
#
# def transfer_format(im, im_format):
#     ret = io.BytesIO()
#     im.save(ret, im_format)
#     return ret.getvalue()
