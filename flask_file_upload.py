import os
from flask import Flask, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import arrow
import errno
import os
from crcs_analyser import on_file_uploaded


UPLOAD_FOLDER = './tmp/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
source_file_path = ""

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def allowed_file(filename):
    return True


def save_source_file(file):
    global source_file_path
    source_file_path = "./source_file/" + arrow.now().format("YYYY_MM_DD")

    if not os.path.exists(source_file_path):
        mkdir_p(source_file_path)

    filename = secure_filename(file.filename)
    file.save(os.path.join(source_file_path, filename))
    pass




@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print 'no file'
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            print 'no filename'
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            #file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            save_source_file(file)
            output_path = "./output_file/" + arrow.now().format("YYYY_MM_DD")
            if not os.path.exists(output_path):
                mkdir_p(output_path)
            app.config['UPLOAD_FOLDER'] = output_path
            ouput_filename = on_file_uploaded(os.path.join(source_file_path, filename), output_path)
            return redirect(url_for('uploaded_file',
                                    filename=ouput_filename))
    return '''
    <!doctype html>
    <title>Upload CRCS File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    print "get output filename:" + filename

    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)


if __name__ == "__main__":
    app.run(debug=True)
