# -*- coding:utf-8 -*-

from PIL import Image
from img_process import *

WATER_MARK_DEFAULT = '/Users/liyouzhi/Pictures/watermark.png'
# WATER_MARK_DEFAULT = '/Users/liyouzhi/Pictures/pexels-photo-205879.jpeg'
im = Image.open('/Users/liyouzhi/Pictures/pexels-photo-273886.jpeg')

def test1():
    watermark = Image.open(WATER_MARK_DEFAULT)
    print('im.size:',im.size)
    print('watermark.size:', watermark.size)

    position = 'right_bottom'

    if position == 'left_top':
        x = 0
        y = 0
    elif position == 'left_bottom':
        x = 0
        y = im.size[1] - watermark.size[1]
    elif position == 'right_top':
        x = im.size[0] - watermark.size[0]
        y = 0
    elif position == 'right_bottom':
        x = im.size[0] - watermark.size[0]
        y = im.size[1] - watermark.size[1]
    else:
        x = (im.size[0] - watermark.size[0])/2
        y = (im.size[1] - watermark.size[1])/2

    layer = Image.new('RGBA', im.size,)
    layer.paste(watermark,(x,y))
    # layer.save('/Users/liyouzhi/Pictures/111111111111111111111111111111111111layer.jpeg')
    # im.paste(watermark,(x,y))
    # im = Image.composite(watermark, im, watermark)
    im = Image.composite(layer, im, layer)
    im.save('/Users/liyouzhi/Pictures/111111111111111111111111111111111111111.jpeg')

def test2():
    im= text2watermark('zimg-python by liyouzhi\n@小玫瑰yui\nhttp://liyouzhi.com')
    im.save('/Users/liyouzhi/Pictures/111111111111111111111111watermark.jpeg')

test2()
