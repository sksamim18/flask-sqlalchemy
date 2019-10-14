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


@app.route('/')
def hello():
    return 'Hello World'


if __name__ == '__main__':
    app.run()