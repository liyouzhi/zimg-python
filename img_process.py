# -*- coding:utf-8 -*-
import math
import logging

from PIL import Image, ImageDraw, ImageFont, ImageFilter

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

def reduce_image(im, ratio):
    w, h = im.size
    w = math.floor(ratio / 100 * w)
    h = math.floor(ratio / 100 * h)
    return im.resize((w,h))

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
def text2watermark(text):
    font_size = 24
    # font_color=(176,173,173,100)
    font_color=(255,255,255,100)
    font = ImageFont.truetype('/System/Library/Fonts/PingFang.ttc', font_size,encoding="unic",index=4)
    text = text.split('\\n')
    print('after:',text)
    mark_width = 0
    n = len(text)
    for i in range(n):
        (width, height) = font.getsize(text[i])
        if mark_width < width: mark_width = width
    mark_height = height * n

    mark = Image.new('RGBA',(mark_width,mark_height))
    draw = ImageDraw.ImageDraw(mark, 'RGBA')
    for i in range(n):
        draw.text((0,i*height),text[i],font=font,fill=font_color)
    # mark = mark.filter(ImageFilter.EDGE_ENHANCE)
    mark = mark.filter(ImageFilter.EDGE_ENHANCE_MORE)
    return mark

def text2watermark2(text):
    font_size = 24
    # font_color=(176,173,173,100)
    font_color=(255,255,255,100)
    font = ImageFont.truetype('/System/Library/Fonts/PingFang.ttc', font_size,encoding="unic",index=4)
    text = text.split('\\n')
    print('after:',text)
    mark_width = 0
    n = len(text)
    for i in range(n):
        (width, height) = font.getsize(text[i])
        if mark_width < width: mark_width = width
    mark_height = height * n

    mark = Image.new('RGBA',(mark_width,mark_height))
    draw = ImageDraw.ImageDraw(mark, 'RGBA')
    for i in range(n):
        draw.text((0,i*height),text[i],font=font,fill=font_color)

    font_color2=(0,0,0,50)
    shadow = Image.new('RGBA',(mark_width,mark_height))
    draw = ImageDraw.ImageDraw(shadow, 'RGBA')
    for i in range(n):
        draw.text((1,i*height),text[i],font=font,fill=font_color2)

    mark = Image.alpha_composite(mark, shadow)

    # mark = mark.filter(ImageFilter.EDGE_ENHANCE)
    mark = mark.filter(ImageFilter.EDGE_ENHANCE_MORE)
    return mark

def watermark_image(im, watermark_im ,position):
    
    if position == 'left_top':
        x = 0
        y = 0
    elif position == 'left_bottom':
        x = 0
        y = im.size[1] - watermark_im.size[1]
    elif position == 'right_top':
        x = im.size[0] - watermark_im.size[0]
        y = 0
    elif position == 'right_bottom':
        x = im.size[0] - watermark_im.size[0]
        y = im.size[1] - watermark_im.size[1]
    else:
        x = (im.size[0] - watermark_im.size[0])/2
        y = (im.size[1] - watermark_im.size[1])/2
    
    x = math.floor(x)
    y = math.floor(y)
    layer = Image.new('RGBA', im.size)
    layer.paste(watermark_im, (x,y))
    return Image.composite(layer, im, layer)

# def watermark_str():
