# -*- coding:utf-8 -*-
import time
import uuid
import os
import magic
import json
import io
import math

from bottle import route, run, template, get, post, request, response, HTTPResponse
from werkzeug.utils import secure_filename
from PIL import Image
import memcache
import redis

from LRUCache import LRUCache

UPLOAD_FOLDER = '/Users/liyouzhi/dev/python/zimg-python/image_storage'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'webp'])

# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  #用户上传文件大小的上限
# cache = LRUCache() #use LRUCache
# cache = memcache.Client(['127.0.0.1:11211'], debug = 1)
cache = redis.StrictRedis(host='127.0.0.1', port=6379, db=1)


def next_id():
    # return '%016d%s%s' % (int(time.time() * 10000), uuid.uuid4().hex, '0'*16)
    return uuid.uuid4().hex


def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def id2address(id):
    addrs = [str(int(id[i:i + 7], 16) % 1024) for i in range(0, 17, 8)]
    print(addrs)
    path = UPLOAD_FOLDER
    # path = app.config['UPLOAD_FOLDER']
    # for addr in addrs:
    #     path = os.path.join(path, addr)
    path = os.path.join(path, '/'.join(addrs))
    print(path)
    return path

# def create_dir(path):
#     addrs = path.split('/')
#     del addrs[0]
#     path = '/'
#     for addr in addrs:
#         path = os.path.join(path, addr)
#         if not os.path.exists(path):
#             os.mkdir(path)
#             print(path,'is created.')
#

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


def resize_image2(im, width, height):
    w, h = im.size
    f = w / h
    if width == 0:
        width = math.floor(height * f)
        if width == 0: width = 1
    if height == 0:
        height = math.floor(width / f)
        if height == 0: height = 1
    return im.resize((width, height))


def crop_image(addr, width, height):
    im = Image.open(addr)
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


# key version
def gen_cache_key(id, w, h, format):
    return 'ick:v0:' + id + ':' + str(w) + ':' + str(h) + ':' + format


@route('/')
def home():
    return template('index.html')

# RESTful api
# http status code
# multipart/form
# curl
# optimize id generator
# timestamp

# inode
# PIL


@post('/images')
def post_image():
    data = request.body.read()
    if not data:
        response.status_code = 400
        return 'upload file not found!'
    mtype = magic.from_buffer(data, mime=True)
    im_type = mtype.split('/')
    if len(im_type) < 2:
        response.status_code = 400
        return 'illegal mimetype!'
    if im_type[1] not in ALLOWED_EXTENSIONS:
        response.status_code = 400
        return 'invalid image format!'
    id = next_id()
    print('id:', id)
    addr = id2address(id)
    # create_dir(addr)
    os.makedirs(addr)
    with open(os.path.join(addr, id), 'wb') as f:
        f.write(data)
    ret = {'key': id}
    return json.dumps(ret)


@post('/images/multipart')
def multipart_post_image():
    file = request.files.get('file')
    if not file:
        response.status_code = 400
        return 'upload file not found'
    if not allowed_file(file.filename):
        response.status_code = 400
        return 'upload file illegal'
    id = next_id()
    addr = id2address(id)
    os.makedirs(addr)
    # create_dir(addr)
    file.save(os.path.join(addr, id))
    ret = {'key': id}
    return json.dumps(ret)


@get('/images/<image_id>')
def get_image(image_id):
    parts = image_id.split('.')
    print(len(parts))
    if len(parts) != 1 and len(parts) != 2:
        return 'invalid request!'
    if len(parts[0]) != 32:
        return 'invalid ID!'

    image_id = parts[0]

    ext = ''
    if len(parts) > 1:
        ext = parts[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            return 'invalid format!'
        if ext == 'jpg': ext = 'jpeg'

    addr = id2address(image_id)
    path = os.path.join(addr, image_id)
    h = int(request.query.h or 0)  #参数大小的限制？
    w = int(request.query.w or 0)
    print('w:', w)
    print('h:', h)
    cache_id = gen_cache_key(image_id, w, h, ext)
    data = None
    if data is None:
        with open(path, 'rb') as f:
            data = f.read()
        need_resize, need_save = False, False
        if h or w or ext:
            imgfile = io.BytesIO(data)
            imgfile.seek(0)
            im = Image.open(imgfile)
            fmt = im.format

            if h or w: need_resize = True
            if need_resize or ext != fmt: need_save = True

            if need_resize:
                im = resize_image2(im, w, h)
            if need_save:
                if ext == '': ext = fmt
                buf = io.BytesIO()
                im.save(buf, ext)
                data = buf.getvalue()

            mtype = 'image/' + ext
        else:
            mtype = magic.from_buffer(data, mime=True)

        # cache.set(cache_id, data)
    else:
        mtype = magic.from_buffer(data, mime=True)

    res = HTTPResponse(body=data)
    res.set_header('Content-Type', mtype)
    return res


if __name__ == '__main__':
    run(host='localhost', port=5000, reloader=True)
