from flask import (
    Flask,
    render_template,
    send_from_directory,
    jsonify,
    request
)
import os
import dotenv
import datetime
import hashlib


ALLOWED_EXTENSIONS = {
    'txt',
    'pdf',
    'png',
    'jpg',
    'jpeg',
    'gif',
    'csv',
    'xlsx',
    'jfif'
}

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000


# /
@app.route('/')
def home():
    return {
        "Routes": [
            "/files",
            "/files/upload"
            "/files/<filename>",
            "/files/download/<filename>",
        ]
    }, 200


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_current_time():
    current_time = datetime.datetime.now()
    time_format = "%Y-%m-%d-%H-%M-%S-%f"
    return current_time.strftime(time_format)


def transform_filename(filename):
    name, extension = filename.rsplit('.', 1)
    name = name + get_current_time()
    return f"{hashlib.md5(name.encode()).hexdigest()}.{extension}"


# /files/upload
@app.route("/files/upload", methods=['GET', 'POST'])
def upload_file():

    if request.method != "POST":
        return render_template('index.html'), 200

    file = request.files.get("filename")

    if file and allowed_file(file.filename):
        transformed_filename = transform_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], transformed_filename))
        return {
            "message": "File uploaded",
            "path": f"/files/{transformed_filename}",
        }, 201
    return {'message': 'You must select a file...'}, 400


# /files/download/<filename>
@app.route("/files/download/<filename>", methods=["GET"])
def download_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)


# /files/<filename>
@app.route("/files/<filename>", methods=["GET"])
def show_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# /files
@app.route("/files", methods=['GET'])
def files_list():
    files = []
    for name in os.listdir(app.config["UPLOAD_FOLDER"]):
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], name)
        if os.path.isfile(file_path):
            files.append(name)
    return jsonify(files)


if __name__ == '__main__':
    dotenv.load_dotenv()
    app.run(debug=True)
