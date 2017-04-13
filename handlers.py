# -*- coding:utf-8 -*-

'url handlers'

# import time
import uuid
import os
import magic
import json
import io
import logging
import re

from bottle import template, request, response, HTTPResponse, abort
from PIL import Image, ImageFilter
import redis

from img_process import *

UPLOAD_FOLDER = '/Users/liyouzhi/dev/python/zimg-python/image_storage'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'webp'])
EXPIRE_TIME = 60 * 15
SETTING_OPTIONS = set(['fill', 'fit', 'stretch'])
POSITIONS = set(['centre', 'left_top', 'left_bottom', 'right_top', 'right_bottom'])
WATER_MARK_DEFAULT = '/Users/liyouzhi/Pictures/watermark.png'

cache = redis.StrictRedis(host='127.0.0.1', port=6379, db=1)


def next_id():
    # return '%016d%s%s' % (int(time.time() * 10000), uuid.uuid4().hex, '0'*16)
    return uuid.uuid4().hex


def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def id2address(id):
    addrs = [str(int(id[i:i + 7], 16) % 1024) for i in range(0, 17, 8)]
    path = UPLOAD_FOLDER
    # path = app.config['UPLOAD_FOLDER']
    # for addr in addrs:
    #     path = os.path.join(path, addr)
    path = os.path.join(path, '/'.join(addrs))
    return path


def gen_cache_key(id, w=0, h=0, format='', s='', a=0, filter='', ratio='', quality='', watermark=0, position=''):
    return 'ick:v0:' + id + ':' + str(w) + ':' + str(
            h) + ':' + format + ':' + s + ':' + str(a) + ':' + filter + ':' + str(ratio) + ':' + quality + ':' + str(watermark) + ':' + position

# def get_cache(cache_id):
#     parts = cache_id.split(':')
#     data = cache.get(cache_id)
#     if data

def home():
    return template('index.html')


def post_image():
    data = request.body.read()
    if not data:
        abort(400, 'upload file not found!')
    mtype = magic.from_buffer(data, mime=True)
    im_type = mtype.split('/')
    if len(im_type) < 2:
        abort(400, 'illegal mimetype!')
    if im_type[1] not in ALLOWED_EXTENSIONS:
        abort(400, 'invalid image formait!')
    id = next_id()
    addr = id2address(id)
    # create_dir(addr)
    os.makedirs(addr)
    with open(os.path.join(addr, id), 'wb') as f:
        f.write(data)
    logging.info('upload image "%s" to "%s"', id, addr)
    ret = {'key': id}
    return json.dumps(ret)


def multipart_post_image():
    file = request.files.get('file')
    if not file:
        abort(400, 'upload file not found!')
    if not allowed_file(file.filename):
        abort(400, 'upload file illegal!')
    id = next_id()
    addr = id2address(id)
    os.makedirs(addr)
    # create_dir(addr)
    file.save(os.path.join(addr, id))
    logging.info('upload image "%s" to "%s"', id, addr)
    ret = {'key': id}
    return json.dumps(ret)


RE_ID = r'^[0-9a-f]{32}$'
RE_ID_EXT = r'^([0-9a-f]{32})\.([a-z]+)$'


def get_image(image_id):
    # parts = image_id.split('.')
    # if len(parts) != 1 and len(parts) != 2:
    #     abort(400, 'invalid request!')
    # if len(parts[0]) != 32:
    #     abort(400, 'invalid ID!')
    #
    # image_id = parts[0]
    #
    #     ext = ''
    # if len(parts) > 1:
    #     ext = parts[1].lower()
    #     if ext not in ALLOWED_EXTENSIONS:
    #         abort(400, 'invalid format!')
    #     if ext == 'jpg': ext = 'jpeg'

    image_id = image_id.lower()
    re_id = re.match(RE_ID, image_id)
    re_id_ext = re.match(RE_ID_EXT, image_id)
    if re_id:
        ext = ''
    elif re_id_ext:
        image_id = re_id_ext.group(1)
        ext = re_id_ext.group(2)
        if ext not in ALLOWED_EXTENSIONS:
            abort(400, 'invalid format!')
    else:
        abort(400, 'invalid request!')
    if ext == 'jpg': ext = 'jpeg'

    addr = id2address(image_id)
    path = os.path.join(addr, image_id)
    h = int(request.query.h or 0)  #参数大小的限制？
    w = int(request.query.w or 0)
    s = request.query.s
    a = int(request.query.a or 0)
    filter = request.query.f 
    ratio = request.query.r
    quality = request.query.q
    watermark = int(request.query.watermark or 0)
    position = request.query.p

    if s and s not in SETTING_OPTIONS:
        abort(400, 'invalid options!')
    if a >= 360:
        abort(400, 'invalid angle!')
    if ratio and (int(ratio) > 100 or int(ratio) < 0):
        abort(400, 'invalid ratio!')
    if quality and (int(quality) > 100 or int(quality) < 0):
        abort(400, 'invalid quality!')
    if watermark:
        if not position:
            position = 'right_bottom'
        elif positon not in POSITIONS:
            abort(400, 'invalid position! valid positions:[centre, left_top, left_bottom, right_top, right_bottom]')

    cache_id = gen_cache_key(image_id, w, h, ext, s, a, filter, ratio, quality, watermark, position)
    data = cache.get(cache_id)
    # data = None
    if data is None:
        data = cache.get(gen_cache_key(image_id))
        if data is None:
            with open(path, 'rb') as f:
                data = f.read()
            logging.info('open image in file: %s', image_id)
        else:
            logging.info('get origin cache: %s',gen_cache_key(image_id))

        need_resize, need_save, need_rotate, need_filter, need_reduce, need_watermark = False, False, False, False, False, False
        if h or w or ratio or a or filter or ext or quality:
            imgfile = io.BytesIO(data)
            imgfile.seek(0)
            im = Image.open(imgfile)
            fmt = im.format

            if a: need_rotate = True
            if filter: need_filter = True
            if h or w: need_resize = True
            if ratio: 
                ratio = int(ratio)
                need_reduce = True
            if watermark: need_watermark=True
            if need_resize or need_rotate or need_filter or ext != fmt or quality or need_watermark: need_save = True

            if need_resize and need_reduce:
                abort(400, "invalid request! can't reduce and resize a image in the same time!")

            if need_resize:
                if s == 'fill':
                    if not h or not w:
                        abort(400, 'fill option needs 2 arguments!')
                    im = fill(im, w, h)
                    logging.info('[fill] (%s) width: %s height: %s', image_id,
                                 w, h)
                elif s == 'fit':
                    if not h or not w:
                        abort(400, 'fit option needs 2 arguments!')
                    im = fit(im, w, h)
                    logging.info('[fit] (%s) width: %s height: %s', image_id,
                                 w, h)
                else:
                    im = resize_image(im, w, h)
                    logging.info('resize (%s) width: %s height: %s', image_id,
                                 w, h)

            if need_reduce:
                im = reduce_image(im, ratio)
                logging.info('reduce (%s) in %d%% ', image_id, ratio)

            if need_rotate:
                im = im.rotate(a)
                logging.info('rotate (%s) angle: %s', image_id, a)


            if need_filter:
                if filter == 'b':
                    im = im.convert('1')
                    logging.info('covert (%s) to black', image_id)
                elif filter == 'bl':
                    im = im.filter(ImageFilter.BLUR)
                    logging.info('filter (%s) with BLUR ', image_id)
                else:
                    abort(400, 'invalid filter!')

            if need_watermark:
                watermark_im = Image.open(WATER_MARK_DEFAULT)
                im = watermark_image(im, watermark_im, position)
                logging.info('default watermark (%s)', image_id)

            if need_save:
                if ext == '': ext = fmt
                buf = io.BytesIO()
                if quality:
                    im.save(buf,ext,quality=int(quality))
                    logging.info('save (%s) as %s, quality:%s', image_id, ext, quality)
                else:
                    im.save(buf, ext)
                    logging.info('save (%s) as %s', image_id, ext)
                data = buf.getvalue()

            mtype = 'image/' + ext
        else:
            mtype = magic.from_buffer(data, mime=True)
            logging.info('get origin image (%s)', image_id)
        cache.set(cache_id, data)
        cache.expire(cache_id, EXPIRE_TIME)
        d = cache.get(cache_id)
        if d != None:
            logging.info('set cache: %s', cache_id)
    else:
        logging.info('get cache: %s', cache_id)
        mtype = magic.from_buffer(data, mime=True)

    res = HTTPResponse(body=data)
    res.set_header('Content-Type', mtype)
    return res
