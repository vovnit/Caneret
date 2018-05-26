import os
from elasticsearch import Elasticsearch
from flask import render_template, request, send_from_directory, send_file, make_response
from hdfs3 import HDFileSystem
from werkzeug.utils import secure_filename
from app import app

es = Elasticsearch({'host': 'localhost', 'port': 9200})
hdfs = HDFileSystem('hdfs://localhost', 8999)

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


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):

    with hdfs.open("/tmp/" + filename, replication=1) as music:
        response = make_response(music.read())
        response.headers.set('Content-Type', 'audio/mpeg')
        response.headers.set('Content-Disposition', 'attachment', filename='%s' % filename)
        response.headers.set('Accept-Ranges', 'bytes')
        return response
    # return send_from_directory(app.config['UPLOAD_FOLDER'],
    #                            filename, as_attachment=True)


