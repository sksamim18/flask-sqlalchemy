import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin


BASE_DIR = os.path.join(os.path.abspath('.'), '.env')
load_dotenv(BASE_DIR)

app = Flask(__name__)
app.config.from_object(os.environ.get('APP_SETTINGS'))
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app)
db = SQLAlchemy(app)

from users.models import *
from prescription.models import *
from users.controllers import *
from prescription.controllers import *
from utils import tools


@app.route('/')
def hello():
    return render_template('index.html')


@app.route('/register', methods=['POST'])
@cross_origin(origin='localhost:3000')
def register():
    response, status = RegisterAPI(request)()
    return jsonify(response), status


@app.route('/login', methods=['POST'])
def login():
    response, status = LoginAPI(request)()
    return jsonify(response), status


@app.route('/edit-user', methods=['POST'])
@tools.login_required
def edit_user():
    response, status = EditUserAPI(request)()
    return jsonify(response), status


@app.route('/edit-user-info', methods=['POST'])
@tools.login_required
def edit_user_info():
    response, status = EditUserInfoAPI(request)()
    return jsonify(response), status


@app.route('/get-past-records', methods=['GET'])
@tools.login_required_doctor
def get_patient_list():
    response, status = GetPastRecords(request)()
    return jsonify(response), status


@app.route('/get-all-medicine', methods=['POST'])
@tools.login_required_pharmacist
def get_all_medicine():
    response, status = GetAllMedicine(request)()
    return jsonify(response), status


@app.route('/remove-medicine', methods=['POST'])
@tools.login_required_pharmacist
def remove_medicine():
    response, status = RemoveMedicine(request)()
    return jsonify(response), status


@app.route('/search-medicine', methods=['GET'])
@tools.login_required_pharmacist
def search_medicine():
    response, status = SearchMedicine(request)()
    return jsonify(response), status


@app.route('/add-medicine', methods=['POST'])
@tools.login_required_pharmacist
def add_medicine():
    response, status = AddMedicine(request)()
    return jsonify(response), status


@app.route('/view-prescription', methods=['GET'])
@tools.login_required
def view_prescription():
    response, status = ViewPrescription(request)()
    return jsonify(response), status


@app.route('/write-prescription', methods=['POST'])
@tools.login_required_doctor
def write_prescription():
    response, status = WritePrescription(request)()
    return jsonify(response), status


@app.route('/get_patient_info', methods=['GET'])
@tools.login_required
def get_patient_info():
    response, status = GetPatientInfo(request)()
    return jsonify(response), status


if __name__ == '__main__':
    app.run()
