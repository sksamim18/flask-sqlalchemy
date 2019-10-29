import random
import hashlib
import uuid
from users import models
from utils import constants
from utils import field_validation
from sqlalchemy.exc import IntegrityError
from app import db
from utils import tools
from dateutil import parser


class RegisterAPI(tools.Request):

    def __init__(self, request):
        super().__init__(request)
        user_type = self.data.get('type')
        if isinstance(user_type, str):
            self.type = self.data.get('type').title()
        else:
            self.type = None

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
        login_type = self.data.get('type', str)
        if isinstance(login_type, str):
            self.login_type = login_type.title()
        else:
            self.login_type = None

    def login_user(self):
        type_error = constants.LOGIN_TYPE_ERROR
        if self.login_type in ['Pharmacy', 'Doctor', 'Patient']:
            response, status = self.login()
        else:
            response, status = type_error, 400
        return response, status

    def login(self):
        data = {}
        validation_error = field_validation.validate_fields(
            self.data, 'LOGIN')
        if validation_error:
            return validation_error, 400
        username = self.data.get('phone_number')
        password = self.data.get('password')
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

        if password != user_instance.password:
            return constants.LOGIN_ERROR, 400

        user_info = self.serilize(user_instance)
        user_mapping_instance = models.UserMapping.query.filter_by(
            user_id=user_instance.id, entity_type=self.login_type).first()
        entity_instance = self.get_entity_instance(user_mapping_instance.entity_id)
        user_details = self.serilize(entity_instance)
        token = str(uuid.uuid4()).replace('-', '')
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
                user_type=user_type,
                token=token
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

    def serilize(self, instance):
        data = {}
        instance = instance.__dict__
        for field, value in instance.items():
            if field not in ['_sa_instance_state', 'password']:
                data[field] = value
        return data

    def __call__(self):
        return self.login_user()


class EditUserAPI(tools.Request):

    def __init__(self, request):
        super().__init__(request)

    def update_user_info(self):
        username = self.data.get('phone_number')
        if not username:
            return {'error': 'Please pass phone number'}, 400
        user_instance = models.User.query.filter_by(username=username).first()
        full_name = self.get_full_name()
        for field, value in full_name.items():
            setattr(user_instance, field, value)
        password = self.data.get('password')
        if password:
            hashed_password = hashlib.sha256(
                password.encode('utf-8')).hexdigest()
            setattr(user_instance, 'password', hashed_password)
        db.session.commit()
        return {'message': 'User updated'}, 200

    def get_full_name(self):
        data = {}
        full_name = self.data.get('full_name')
        if not full_name:
            return {}
        else:
            full_name = full_name.split(' ')
        if len(full_name) >= 1:
            data['first_name'] = full_name[0]
        if len(full_name) == 3:
            data['middle_name'] = full_name[1]
        if len(full_name) >= 2:
            data['last_name'] = full_name[-1]
        return data

    def __call__(self):
        return self.update_user_info()


class EditUserInfoAPI(tools.Request):

    def __init__(self, request):
        super().__init__(request)
        user_type = self.data.get('type')
        if isinstance(user_type, str):
            self.user_type = user_type.title()
        else:
            self.user_type = None

    def update_user_details_info(self):
        import pdb; pdb.set_trace()
        if self.user_type == 'Patient':
            response, status = self.update_patient()
        elif self.user_type == 'Doctor':
            response, status = self.update_doctor()
        elif self.user_type == 'Pharmacist':
            response, status = self.update_pharmacy()
        else:
            response, status = constants.MISSING_TYPE_ERROR, 400
        return response, status

    def update_patient(self):
        data = {}
        dob = self.data.get('dob')
        address = self.data.get('address')
        gender = self.data.get('gender').upper()

        entity_instance = self.get_entity_instance()
        if not entity_instance:
            return {'error': 'User does not exist'}, 400

        validation_error = field_validation.validate_update_fields(
            self.data, 'UPDATE_USER_PATIENT')
        if validation_error:
            return validation_error, 400
        if dob:
            data['dob'] = parser.parse(dob)
        if address:
            data['address'] = address
        if gender:
            data['gender'] = gender
        for field, value in data.items():
            setattr(entity_instance, field, value)
        db.session.commit()
        return {'message': "User successfully updated."}, 200

    def update_doctor(self):
        data = {}
        nickname = self.data.get('nickname')
        qualification = self.data.get('qualification')
        work_ex = self.data.get('work_ex')
        address = self.data.get('address')
        account_status = self.data.get('account_status')
        entity_instance = self.get_entity_instance()

        validation_error = field_validation.validate_update_fields(
            self.data, 'UPDATE_USER_DOCTOR')

        if validation_error:
            return validation_error, 400
        if not entity_instance:
            return {'error': 'User does not exist'}, 400

        if nickname:
            data['nickname'] = nickname
        if qualification:
            data['qualification'] = qualification
        if work_ex:
            data['work_ex'] = work_ex
        if address:
            data['address'] = address
        if account_status and account_status in ['active', 'deactive']:
            data['account_status'] = account_status

        for field, value in data.items():
            setattr(entity_instance, field, value)
        db.session.commit()
        return {'message': "User successfully updated."}, 200

    def update_pharmacy(self):
        import pdb; pdb.set_trace()
        data = {}
        shop_name = self.data.get('shop_name')
        cerification = self.data.get('cerification')
        work_ex = self.data.get('work_ex')
        opening_time = self.data.get('opening_time')
        closing_time = self.data.get('closing_time')
        address = self.data.get('address')
        account_status = self.data.get('account_status')
        entity_instance = self.get_entity_instance()
        validation_error = field_validation.validate_update_fields(
            self.data, 'UPDATE_USER_PHARMACY')

        if validation_error:
            return validation_error, 400
        if not entity_instance:
            return {'error': 'User does not exist'}, 400

        if shop_name:
            data['shop_name'] = shop_name
        if cerification:
            data['cerification'] = cerification
        if work_ex:
            data['work_ex'] = work_ex
        if opening_time:
            data['opening_time'] = opening_time
        if closing_time:
            data['closing_time'] = closing_time
        if address:
            data['address'] = address
        if account_status and isinstance(account_status, str):
            data['account_status'] = account_status

        for field, value in data.items():
            setattr(entity_instance, field, value)
        db.session.commit()
        return {'message': "User successfully updated."}, 200

    def get_entity_instance(self):
        import pdb; pdb.set_trace()
        try:
            user_map_instance = models.UserMapping.query.filter_by(
                user_id=self.get_user_instance,
                entity_type=self.user_type).first()
            entity_instance = getattr(models, self.user_type).query.filter_by(
                id=user_map_instance.entity_id).first()
        except Exception:
            return
        return entity_instance

    def __call__(self):
        return self.update_user_details_info()
