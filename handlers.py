# -*- coding:utf-8 -*-

'url handlers'

# import time
import uuid
import os
import magic
import json
import io
import logging

from bottle import route, run, template, get, post, request, response, HTTPResponse, abort
from PIL import Image

from img_process import *

UPLOAD_FOLDER = '/Users/liyouzhi/dev/python/zimg-python/image_storage'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'webp'])


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


def gen_cache_key(id, w, h, format):
    return 'ick:v0:' + id + ':' + str(w) + ':' + str(h) + ':' + format


@route('/')
def home():
    return template('index.html')


@post('/images')
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
    logging.info('upload image "%s" to "%s"', id, addr)
    ret = {'key': id}
    return json.dumps(ret)


@get('/images/<image_id>')
def get_image(image_id):
    parts = image_id.split('.')
    if len(parts) != 1 and len(parts) != 2:
        abort(400, 'invalid request!')
    if len(parts[0]) != 32:
        abort(400, 'invalid ID!')

    image_id = parts[0]

    ext = ''
    if len(parts) > 1:
        ext = parts[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            abort(400, 'invalid format!')
        if ext == 'jpg': ext = 'jpeg'

    addr = id2address(image_id)
    path = os.path.join(addr, image_id)
    h = int(request.query.h or 0)  #参数大小的限制？
    w = int(request.query.w or 0)
    cache_id = gen_cache_key(image_id, w, h, ext)
    data = None
    # date = cache.get(cache_id)
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
                logging.info('resize (%s) width: %s height: %s', image_id, w,
                             h)
            if need_save:
                if ext == '': ext = fmt
                buf = io.BytesIO()
                im.save(buf, ext)
                data = buf.getvalue()
                logging.info('save (%s) as %s', image_id, ext)

            mtype = 'image/' + ext
        else:
            mtype = magic.from_buffer(data, mime=True)
            logging.info('get origin image (%s)', image_id)

        # cache.set(cache_id, data)
    else:
        logging.info('get cache: %s', cache_id)
        mtype = magic.from_buffer(data, mime=True)

    res = HTTPResponse(body=data)
    res.set_header('Content-Type', mtype)
    return res