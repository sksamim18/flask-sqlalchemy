import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy


BASE_DIR = os.path.join(os.path.abspath('.'), '.env')
load_dotenv(BASE_DIR)

app = Flask(__name__)
app.config.from_object(os.environ.get('APP_SETTINGS'))
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
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


@app.route('/get-patient-info', methods=['POST'])
@tools.login_required_doctor
def get_patient_list():
    response, status = GetPatientList(request)()
    return response, status


@app.route('/get-all-medicine', methods=['POST'])
@tools.login_required_pharmacist
def get_all_medicine():
    response, status = GetAllMedicine(request)()
    return response, status


@app.route('/update-medicine', methods=['POST'])
@tools.login_required_pharmacist
def update_medicine():
    response, status = UpdateMedicine(request)()
    return response, status


@app.route('/remove-medicine', methods=['POST'])
@tools.login_required_pharmacist
def remove_medicine():
    response, status = RemoveMedicine(request)()
    return response, status


@app.route('/search-medicine', methods=['GET'])
@tools.login_required_pharmacist
def search_medicine():
    response, status = SearchMedicine(request)()
    return response, status


@app.route('/add-medicine', methods=['POST'])
@tools.login_required_pharmacist
def add_medcine():
    response, status = AddMedcine(request)()
    return response, status


@app.route('/view-prescription', methods=['GET'])
@tools.login_required
def view_prescription():
    response, status = ViewPrescription(request)()
    return response, status


@app.route('/write-prescription')
@tools.login_required_doctor
def write_prescription():
    response, status = WritePrescription(request)()
    return response, status

if __name__ == '__main__':
    app.run()
