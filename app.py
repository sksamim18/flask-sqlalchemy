import os

from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


BASE_DIR = os.path.join(os.path.abspath('.'), '.env')
load_dotenv(BASE_DIR)

app = Flask(__name__)
app.config.from_object(os.environ.get('APP_SETTINGS'))
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
db = SQLAlchemy(app)

from users.models import *
from users import controllers
from flask import jsonify, request


@app.route('/')
def hello():
    return 'Hello World'


@app.route('/register', methods=['POST'])
def register():
    response, status = controllers.RegisterAPI(request)()
    return jsonify(response), status


@app.route('/login', methods=['POST'])
def login():
    response, status = controllers.LoginAPI(request)()
    return jsonify(response), status


if __name__ == '__main__':
    app.run()