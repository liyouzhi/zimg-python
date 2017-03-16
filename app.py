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
#    return '%016d%s%s' % (int(time.time() * 10000), uuid.uuid4().hex, '0'*16)
    return uuid.uuid4().hex

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def id2address(id):
    addr = [str(int(id[i:i+7], 16) % 1024) for i in range(0,17,8)]
    print(addr)
    path = app.config['UPLOAD_FOLDER']
    for a in addr:
        path = os.path.join(path, a)
    print(path)
    return path

def id2address_upload(id):
    addr = [str(int(id[i:i+7], 16) % 1024) for i in range(0,17,8)]
    path = app.config['UPLOAD_FOLDER']
    for a in addr:
        path = os.path.join(path, a)
        if not os.path.exists(path):
            os.mkdir(path)
    return path 

def resize_by_weight(addr, weight):
    im = Image.open(addr)
    w, h = im.size
    height = int(weight * h / w)
    out = im.resize((weight, height))
    ret = io.BytesIO()
    out.save(ret, im.format)
    return ret.getvalue()

def resize_by_height(addr, height):
    im = Image.open(addr)
    w, h = im.size
    weight = int(height * w / h)
    out = im.resize((weight, height))
    ret = io.BytesIO()
    out.save(ret, im.format)
    return ret.getvalue()

def resize_by_wh(addr, weight, height):
    im = Image.open(addr)
    #out = im.resize((weight, height))
    w, h = im.size
    region = ((w-weight)/2, (h-height)/2, (w+weight)/2, (h+height)/2)
    out = im.crop(region)
    ret = io.BytesIO()
    out.save(ret, im.format)
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
    addr = id2address_upload(id)
    with open(os.path.join(addr, id), 'wb') as f:
        f.write(data)
    ret = { 'key': id }
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
    addr = id2address_upload(id)
    file.save(os.path.join(addr, id))
    ret = { 'key': id }
    return json.dumps(ret)

@app.route('/images/<image_id>', methods=['GET'])
def get_image(image_id):
    if len(image_id) != 32:
        return 'invalid ID!'
    addr = id2address(image_id)
    path = os.path.join(addr, image_id)
    h = request.args.get('h')
    w = request.args.get('w')
    if h and w:
        h = int(h)
        w = int(w)
        data = resize_by_wh(path, w, h)
    elif h:
        h = int(h)
        data = resize_by_height(path, h)
    elif w:
        w = int(w)
        data = resize_by_weight(path, w)
    else:
        with open(path, 'rb') as f:
            data = f.read()
    mtype = magic.from_buffer(data, mime=True)
    response = make_response(data)
    response.headers['Content-Type'] = mtype
    return response

if __name__ == '__main__':
    app.run(debug=True)

