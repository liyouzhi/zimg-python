# -*- coding:utf-8 -*-
import time
import uuid
import os
import magic
import json
import io

from flask import Flask, render_template
from flask import request
from flask import send_from_directory, make_response
from werkzeug.utils import secure_filename
from PIL import Image
import memcache
import redis

from LRUCache import LRUCache

UPLOAD_FOLDER = '/Users/liyouzhi/dev/python/zimg-python/image_storage'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'webp'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  #用户上传文件大小的上限
# cache = LRUCache() #use LRUCache
# cache = memcache.Client(['127.0.0.1:11211'], debug = 1)
cache = redis.StrictRedis(host='127.0.0.1', port=6379, db=1)


def next_id():
    # return '%016d%s%s' % (int(time.time() * 10000), uuid.uuid4().hex, '0'*16)
    return uuid.uuid4().hex


def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def id2address(id):
    addrs = [str(int(id[i:i + 7], 16) % 1024) for i in range(0, 17, 8)]
    print(addrs)
    path = app.config['UPLOAD_FOLDER']
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


def resize_image(addr, weight, height):
    im = Image.open(addr)
    w, h = im.size
    if weight == 0:
        weight = int(height * w / h)
    if height == 0:
        height = int(weight * h / w)
    out = im.resize((weight, height))
    # ret = io.BytesIO()
    # out.save(ret, im.format)
    # return ret.getvalue()
    return out


def crop_image(addr, weight, height):
    im = Image.open(addr)
    w, h = im.size
    region = ((w - weight) / 2, (h - height) / 2, (w + weight) / 2,
              (h + height) / 2)
    out = im.crop(region)
    # ret = io.BytesIO() 
    # out.save(ret, im.format) 
    # return ret.getvalue() 
    return out


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


def get_cache_key(id, w, h, format):
    return id + ':' + str(w) + ':' + str(h) + ':' + format


@app.route('/')
def home():
    return render_template('index.html')


# RESTful api
# http status code
# multipart/form
# curl
# optimize id generator
# timestamp

# inode
# PIL


@app.route('/images', methods=['POST'])
def post_image():
    data = request.get_data()
    if not data:
        response.status_code = 400
        return 'upload file not found!'
    mtype = magic.from_buffer(data, mime=True)
    im_type = mtype.split('/')
    if im_type[1] not in ALLOWED_EXTENSIONS:
        response.status_code = 400
        return 'invalid image format!'
    id = next_id()
    print('id:', id)
    addr = id2address(id)
    create_dir(addr)
    with open(os.path.join(addr, id), 'wb') as f:
        f.write(data)
    ret = {'key': id}
    return json.dumps(ret)


@app.route('/images/multipart', methods=['POST'])
def multipart_post_image():
    file = request.files['file']
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


# /images/id.jpeg?w=x&h=y
# LRU cache: private/memcache/redis
@app.route('/images/<image_id>', methods=['GET'])
def get_image(image_id):
    image = image_id.split('.')
    print(len(image))
    if len(image) != 1 and len(image) != 2:
        return 'invalid request!'
    if len(image[0]) != 32:
        return 'invalid ID!'
    if len(image) == 2:
        ntype = image[1].lower()
        if ntype not in ALLOWED_EXTENSIONS:
            return 'invalid format!'
        if ntype == 'jpg':
            ntype = 'jpeg'
    else:
        ntype = ''
    addr = id2address(image[0])
    path = os.path.join(addr, image[0])
    h = int(request.args.get('h') or 0)  #参数大小的限制？
    w = int(request.args.get('w') or 0)
    cache_id = get_cache_key(image[0], w, h, ntype)
    data = cache.get(cache_id) 
    if data == None:
        if not h and not w and not ntype:
            with open(path, 'rb') as f:
                data = f.read()
                mtype = magic.from_buffer(data, mime=True)
        else:
            if h or w:
                im = resize_image(path, w, h)
                if not ntype:
                    ntype ='webp' 
            else:
                im = Image.open(path)
            ret = io.BytesIO()
            im.save(ret, ntype)
            data = ret.getvalue()
            mtype = 'image/' + ntype
        cache.set(cache_id, data)
    else:
        mtype = magic.from_buffer(data, mime=True)
    response = make_response(data)
    response.headers['Content-Type'] = mtype
    return response


if __name__ == '__main__':
    app.run(debug=True)
