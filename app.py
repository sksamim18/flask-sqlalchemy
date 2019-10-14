# from flask import Flask
# from flask import jsonify
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate, MigrateCommand
# from flask_script import Manager

# from config import settings

# app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = settings.connection_string
# db = SQLAlchemy(app)

# migrate = Migrate(app, db)
# manager = Manager(app)
# manager.add_command('db', MigrateCommand)

# if __name__ == '__main___':
#     app.run()


import os

from dotenv import load_dotenv
from flask import Flask


BASE_DIR = os.path.join(os.path.abspath('.'), '.env')
load_dotenv(BASE_DIR)

app = Flask(__name__)
app.config.from_object(os.environ.get('APP_SETTINGS'))


@app.route('/')
def hello():
    return 'Hello World'


if __name__ == '__main__':
    app.run()