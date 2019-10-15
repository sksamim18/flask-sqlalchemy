import random
import hashlib
from users import models
from utils import constants
from utils import field_validation
from sqlalchemy.exc import IntegrityError
from app import db
from utils import tools


generate_random = lambda x: str(random.randint(0, 9))


class RegisterAPI(tools.Request):

    def __init__(self, request):
        super().__init__(request)
        self.type = self.data.get('type').title()

    def create_user(self):
        status = 400
        error = constants.REGISTRATION_ERROR
        if self.type == 'Patient':
            response, status = self.register_patient()
        elif self.type == 'Pharmacy':
            response, status = self.register_pharmacy()
        elif self.type == 'Doctor':
            response, status = self.register_doctor()
        else:
            return error, status
        return response, status

    def register_patient(self):
        validation_error = field_validation.validate_fields(
            self.data, 'PATIENT_REGISTRATION')
        if validation_error:
            return validation_error, 400

        user_instance = self.get_or_create_user()
        patient_instance = models.Patient(address="")
        db.session.add(patient_instance)
        db.session.commit()
        try:
            user_mapping_instance = models.UserMapping(
                user_id=user_instance.id,
                entity_id=patient_instance.id,
                entity_type=self.type)
            db.session.add(user_mapping_instance)
            db.session.commit()
        except (IntegrityError):
            db.session.rollback()
            db.session.delete(patient_instance)
            db.session.commit()
            return {'error': 'User already exists.'}, 400
        return {'message': 'User successfully created'}, 201

    def register_pharmacy(self):
        data = {}
        validation_error = field_validation.validate_fields(
            self.data, 'PHARMACY_REGISTRATION')

        if validation_error:
            return validation_error, 400

        user_instance = self.get_or_create_user()
        data['work_ex'] = self.data.get('work_ex')
        data['cerification'] = self.data.get('cerification')
        pharmacist_instance = models.Pharmacist(**data)
        db.session.add(pharmacist_instance)
        db.session.commit()

        try:
            user_mapping_instance = models.UserMapping(
                user_id=user_instance.id,
                entity_id=pharmacist_instance.id,
                entity_type=self.type)
            db.session.add(user_mapping_instance)
            db.session.commit()
        except (IntegrityError, ):
            db.session.rollback()
            db.session.delete(pharmacist_instance)
            db.session.commit()
            return {'error': 'User already exists'}, 400
        return {'message': 'User successfully created'}, 201

    def register_doctor(self):
        data = {}
        validation_error = field_validation.validate_fields(
            self.data, 'DOCTOR_REGISTRATION')

        if validation_error:
            return validation_error, 400

        user_instance = self.get_or_create_user()
        data['work_ex'] = self.data.get('work_ex')
        data['qualification'] = self.data.get('qualification')
        doctor_instance = models.Doctor(**data)
        db.session.add(doctor_instance)
        db.session.commit()

        try:
            user_mapping_instance = models.UserMapping(
                user_id=user_instance.id,
                entity_id=doctor_instance.id,
                entity_type=self.type)
            db.session.add(user_mapping_instance)
            db.session.commit()
        except (IntegrityError, ):
            db.session.rollback()
            db.session.delete(doctor_instance)
            db.session.commit()
            return {'error': 'User already exists'}, 400

        return {'message': 'User successfully created'}, 201

    def get_or_create_user(self):
        data = {}
        phone_number = self.data.get('phone_number')
        user_instance = models.User.query.filter_by(
            username=phone_number).first()

        if user_instance:
            return user_instance

        data.update(self.get_full_name())
        data['username'] = phone_number
        data['password'] = hashlib.sha256(self.data.get(
            'password').encode('utf-8')).hexdigest()
        user_instance = models.User(**data)
        db.session.add(user_instance)
        db.session.commit()
        return user_instance

    def get_full_name(self):
        data = {}
        full_name = self.data.get('full_name').split(' ')
        if len(full_name) >= 1:
            data['first_name'] = full_name[0]
        if len(full_name) == 3:
            data['middle_name'] = full_name[1]
        if len(full_name) >= 2:
            data['last_name'] = full_name[-1]
        return data

    def __call__(self):
        return self.create_user()


class LoginAPI(tools.Request):

    def __init__(self, request):
        super().__init__(request)
        self.login_type = self.data.get('type', str()).title()

    def login_user(self):
        type_error = constants.LOGIN_TYPE_ERROR
        if self.login_type in ['Pharmacy', 'Doctor', 'Patient']:
            response, status = self.login()
        else:
            response, status = type_error, 400
        return response, status

    def login(self):
        data = {}
        username = self.data.get('phone_number')
        password = self.data.get('password')
        validation_error = field_validation.validate_fields(
            self.data, 'LOGIN')
        if validation_error:
            return validation_error, 400
        password = hashlib.sha256(password.encode('utf-8')).hexdigest()

        try:
            user_instance = models.User.query.filter_by(
                username=username).first()
            user_mapping_instance = models.UserMapping.query.filter_by(
                user_id=user_instance.id,
                entity_type=self.login_type).first()
            if not user_mapping_instance:
                return {'error': 'User not found'}, 400
        except:
            return {'error': 'User not found'}, 400

        user_info = self.serilize(user_instance)
        if password != user_instance.password:
            return constants.LOGIN_ERROR, 400
        user_mapping = models.UserMapping.query.filter_by(
            user_id=user_instance.id, entity_type=self.login_type).first()
        entity_instance = self.get_entity_instance(user_mapping.entity_id)
        user_details = self.serilize(entity_instance)
        token = ''.join(list(map(generate_random, range(32))))
        token_instance = self.get_token_instance(
            user_instance.id, token, self.login_type)
        db.session.add(token_instance)
        db.session.commit()
        data['user_info'] = user_info
        data['user_details'] = user_details
        data['auth_token'] = token
        return data, 200

    def get_token_instance(self, user_id, token, user_type):
        token_instance = models.AuthToken.query.filter_by(
            user_id=user_id,
            user_type=user_type).first()
        if token_instance:
            token_instance.token = token
        else:
            token_instance = models.AuthToken(
                user_id=user_id,
                user_type=user_type
            )
        db.session.add(token_instance)
        db.session.commit()
        return token_instance

    def get_entity_instance(self, id):
        if self.login_type == 'Patient':
            return models.Patient.query.filter_by(id=id).first()
        elif self.login_type == 'Doctor':
            return models.Doctor.query.filter_by(id=id).first()
        elif self.login_type == 'Pharmacy':
            return models.Pharmacist.query.filter_by(id=id).first()

    def serilize(self, user_instance):
        data = {}
        user_instance = user_instance.__dict__
        for field, value in user_instance.items():
            if field not in ['_sa_instance_state', 'password']:
                data[field] = value
        return data

    def __call__(self):
        return self.login_user()
