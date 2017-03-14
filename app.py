# -*- coding:utf-8 -*-

from flask import Flask, render_template
from flask import request
from flask import send_from_directory, make_response
from werkzeug.utils import secure_filename

import time
import uuid
import os

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

@app.route('/<image_id>', methods=['GET'])
def get_image(image_id):
    if len(image_id) == 64:
        return '<img src="%s" />' % os.path.join(app.config['UPLOAD_FOLDER'], image_id)

@app.route('/download/<image_id>')
def download_image(image_id):
    return send_from_directory(app.config['UPLOAD_FOLDER'], image_id)

@app.route('/upload', methods=['POST'])
def upload_image():
    file = request.files['file']
    if file and allowed_file(file.filename):
        id = next_id()
        #file.filename = secure_filename(id)
        file.filename = id + '.' + file.filename.rsplit('.', 1)[1]
        #print('filename:', file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        return '<h3>key: %s<h3>' % id

if __name__ == '__main__':
    app.run(debug=True)


