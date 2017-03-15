# -*- coding:utf-8 -*-
import time
import uuid
import os
import magic
import json

from flask import Flask, render_template
from flask import request
from flask import send_from_directory, make_response
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/Users/liyouzhi/dev/python/zimg-python/image_storage'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def next_id():
    return '%016d%s%s' % (int(time.time() * 10000), uuid.uuid4().hex, '0'*16)

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('index.html')


# RESTful api
# http status code
# multipart/form
# curl
# optimize id generator
# timestamp

@app.route('/images', methods=['POST'])
def post_image():
    data = request.get_data()
    id = next_id()
    print('id:', id)
    with open(os.path.join(app.config['UPLOAD_FOLDER'], id), 'wb') as f:
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
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], id))
    ret = { 'key': id }
    return json.dumps(ret)

@app.route('/images/<image_id>', methods=['GET'])
def get_image(image_id):
    with open(os.path.join(app.config['UPLOAD_FOLDER'], image_id), 'rb') as f:
        data = f.read()
    mtype = magic.from_buffer(data, mime=True)
    response = make_response(data)
    response.headers['Content-Type'] = mtype
    return response

@app.route('/download/<image_id>')
def download_image(image_id):
    return send_from_directory(app.config['UPLOAD_FOLDER'], image_id)

if __name__ == '__main__':
    app.run(debug=True)

