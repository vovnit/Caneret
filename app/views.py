import os
from elasticsearch import Elasticsearch
from flask import render_template, request, send_from_directory, send_file, make_response
from hdfs3 import HDFileSystem
from werkzeug.utils import secure_filename
from app import app


es = Elasticsearch({'host': 'localhost', 'port': 9200})
hdfs = HDFileSystem('hdfs://localhost', 9000)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file.filename:
            filename = secure_filename(file.filename)
            hdfs.touch("/tmp/%s"%filename)
            with hdfs.open("/tmp/%s"%filename, mode="wb") as f:
                f.write(file.read())

            return render_template('index.html', filename=filename)
    return render_template('upload.html')

def make_audio(path):
    with hdfs.open(path, replication=1) as music:
        response = make_response(music.read())
        response.headers.set('Content-Type', 'audio/mpeg')
        response.headers.set('Content-Disposition', 'attachment', filename='%s' % path)
        response.headers.set('Accept-Ranges', 'bytes')
        return response


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return make_audio("/tmp/" + filename)

    # return send_from_directory(app.config['UPLOAD_FOLDER'],
    #                            filename, as_attachment=True)


@app.route('/music')
def music():
    res = []
    for it in hdfs.ls('/tmp/'):
        res.append(it[5:])
    return render_template('music.html', music=res)