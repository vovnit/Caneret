import os
from flask import render_template, request, send_from_directory, send_file, make_response
from hdfs3 import HDFileSystem
from werkzeug.utils import secure_filename
from app import app


hdfs = HDFileSystem('localhost', 9000)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    os.environ["HADOOP_CONF_DIR"] = "/home/vovnit/Soft/hadoop-3.1.0/etc/hadoop"
    if request.method == 'POST':
        file = request.files['file']
        if file.filename:
            filename = secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)
            hdfs.put(path, "/tmp/%s"%filename, replication=1)
            os.remove(path)
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
