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

UPLOAD_FOLDER = '/Users/liyouzhi/dev/python/zimg-python/image_storage'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


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
    ret = io.BytesIO()
    out.save(ret, im.format)
    return ret.getvalue()

def crop_image(addr, weight, height):
    im = Image.open(addr) 
    w, h = im.size 
    region = ((w - weight) / 2, (h - height) / 2, (w + weight) / 2, (h + height) / 2) 
    out = im.crop(region) 
    ret = io.BytesIO() 
    out.save(ret, im.format) 
    return ret.getvalue() 

def transfer_format(im_data, im_format):
    im = Image.open(io.BytesIO(im_data))
    ret = io.BytesIO()
    im.save(ret, im_format)
    return ret.getvalue()

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
    elif len(image[0]) != 32:
        return 'invalid ID!'
    addr = id2address(image[0])
    path = os.path.join(addr, image[0])
    h = int(request.args.get('h') or 0)
    w = int(request.args.get('w') or 0)
    if h or w:
        data = resize_image(path, w, h)
    else:
        with open(path, 'rb') as f:
            data = f.read()
    mtype = magic.from_buffer(data, mime=True)
    if len(image) == 2:
        if image[1] not in ALLOWED_EXTENSIONS:
            return 'invalid format!'
        if image[1] == 'jpg':
            image[1] = 'jpeg'
        itype = mtype.split('/')[1]
        if image[1] != itype:
            data = transfer_format(data, image[1])
            mtype = 'image/' + image[1]
    response = make_response(data)
    response.headers['Content-Type'] = mtype
    return response


if __name__ == '__main__':
    app.run(debug=True)
