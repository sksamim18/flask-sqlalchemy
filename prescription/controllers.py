import hashlib
from datetime import datetime
from dateutil import parser
from collections import defaultdict
from prescription import models as prescription_model
from users import models as user_model
from utils import tools
from app import db
from utils import field_validation
from sqlalchemy.exc import IntegrityError


class GetPastRecords(tools.Request):

    def __init__(self, request):
        super().__init__(request)

    def get_patient_list(self):
        # Query Optimisation
        type = self.args.get('type')
        if type not in ['patient', 'prescription']:
            return {'error': 'Please pass in proper data type.'}, 400
        data = []
        patient_ids = []
        prescription_ids = []
        patient_dict = {}
        diagnosis_dict = defaultdict(list)
        doctor_id = self.args.get('doctor_id')
        prescription_instances = prescription_model.Prescription.query.filter_by(
            doctor_id=doctor_id)
        for prescription in prescription_instances:
            prescription_ids.append(prescription.id)
            patient_ids.append(prescription.patient_id)
        diagnosis_instances = prescription_model.Diagnosis.query.filter(
            prescription_model.Diagnosis.prescription_id.in_(prescription_ids))
        patient_instances = user_model.User.query.filter(
            user_model.User.id.in_(patient_ids))
        for field in diagnosis_instances:
            diagnosis_dict[field.prescription_id].append(field.cause)
        for field in patient_instances:
            patient_dict[field.id] = field.full_name
        for prescription in prescription_instances:
            fields = {}
            fields['patient_name'] = patient_dict.get(prescription.patient_id)
            if type.lower() == 'patient':
                fields['timestamp'] = prescription.timestamp
            if type.lower() == 'prescription':
                fields['prescription_id'] = prescription.id
            diagnosis = diagnosis_dict.get(prescription.id)
            fields['diagnosis'] = diagnosis
            data.append(fields)
        return data, 200

    def __call__(self):
        return self.get_patient_list()


class UpdateMedicine(tools.Request):

    def __init__(self, request):
        super().__init__(request)

    def update_medicine(self):
        validation_error = field_validation.validate_fields(
            self.data, 'UPDATE_MEDICINE')
        if validation_error:
            return validation_error, 400
        user_id = self.get_user_instance
        data = {}
        data['user_id'] = user_id
        data['medicine_id'] = self.data.get('medicine_id')
        data['in_stock'] = self.data.get('in_stock')
        available_medicine_instance = models.AvailableMedicine(**data)
        db.session.add(available_medicine_instance)
        db.session.commit()

    def __call__(self):
        return self.update_medicine()


class RemoveMedicine(tools.Request):

    def __init__(self, request):
        super().__init__(request)

    def remove_medicine(self):
        sold_unit = self.data.get('sold_unit')
        medicine_id = self.data.get('medicine_id')

        medicine_instance = prescription_model.Medicine.query.filter_by(
            id=medicine_id).first()
        available_medicine_instance = prescription_model.AvailableMedicine.query.filter_by(
            pharmacist_id=self.get_user_instance,
            medicine_id=medicine_instance.id).first()
        left_out_medicine = available_medicine_instance.in_stock - sold_unit
        if left_out_medicine < 0:
            return {'error': 'Quantity unavailable'}, 400
        available_medicine_instance.in_stock = left_out_medicine
        db.session.commit()
        return {'message': 'Successfully updated'}, 200

    def __call__(self):
        return self.remove_medicine()


class SearchMedicine(tools.Request):

    def __init__(self, request):
        super().__init__(request)

    def search_medicine(self):
        data, medicine_ids = [], []
        query = self.args.get('q')
        available_instances = prescription_model.AvailableMedicine.query.filter_by(
            pharmacist_id=self.get_user_instance)
        medicine_ids = [medicine.id for medicine in available_instances]
        medicine_instances = prescription_model.Medicine.query.filter(
            prescription_model.Medicine.id.in_(medicine_ids))
        medicine_instances = medicine_instances.filter(
            prescription_model.Medicine.title.startswith(query))
        for medicine in medicine_instances:
            medicine_data = {}
            medicine_data['id'] = medicine.id
            medicine_data['title'] = medicine.title
            medicine_data['details'] = medicine.details
            data.append(medicine_data)
        return data, 200

    def __call__(self):
        return self.search_medicine()


class AddMedicine(tools.Request):

    def __init__(self, request):
        super().__init__(request)

    def add_medicine(self):
        data = {}
        data['in_stock'] = self.data.get('in_stock')
        data['medicine_id'] = self.data.get('medicine_id')
        data['pharmacist_id'] = self.get_user_instance
        available_medicine_instance = prescription_model.AvailableMedicine(
            **data)
        db.session.add(available_medicine_instance)
        db.session.commit()
        return {'message': 'Medicine updated successfully.'}, 201

    def __call__(self):
        return self.add_medicine()


class ViewPrescription(tools.Request):

    def __init__(self, request):
        super().__init__(request)

    def get_prescription(self):
        data, diagnosis_list, treatment_list = {}, [], []
        prescription_id = self.args.get('prescription_id')

        prescription_instance = prescription_model.Prescription.query.get(
            prescription_id)
        patient_user_instance = user_model.User.query.get(
            prescription_instance.patient_id)
        patient_map_instance = user_model.UserMapping.query.filter_by(
            user_id=patient_user_instance.id,
            entity_type='Patient').first()
        patient_instance = user_model.Patient.query.get(
            patient_map_instance.entity_id)
        doctor_user_instance = user_model.User.query.get(
            prescription_instance.doctor_id)
        doctors_map_instance = user_model.UserMapping.query.filter_by(
            id=doctor_user_instance.id,
            entity_type='Doctor').first()
        doctor_instance = user_model.Doctor.query.get(
            doctors_map_instance.entity_id)
        diagnosis_instances = prescription_model.Diagnosis.query.filter_by(
            prescription_id=prescription_id)
        treatment_instances = prescription_model.Treatment.query.filter_by(
            prescription_id=prescription_id)
        for diagnosis in diagnosis_instances:
            diagnosis_list.append({
                'id': diagnosis.id,
                'cause': diagnosis.cause
            })
        for treatment in treatment_instances:
            treatment_list.append({
                'id': treatment.id,
                'medication': treatment.medication
            })
        data['diagnosis'] = diagnosis_list
        data['treatment'] = treatment_list
        data['patient'] = {
            'full_name': patient_user_instance.full_name,
            'patientID': patient_user_instance.phone_number,
            'patient_age': patient_instance.age,
            'patient_gender': patient_instance.gender
        }
        data['doctor'] = {
            'full_name': doctor_user_instance.full_name,
            'doctorID': doctor_user_instance.phone_number,
            'qualification': doctor_instance.qualification
        }
        return data, 200

    def __call__(self):
        return self.get_prescription()


class WritePrescription(tools.Request):

    def __init__(self, request):
        super().__init__(request)
        self.patient_instance = None

    def write_prescription(self):
        data = {}
        doctor_instance = self.get_user_instance
        data['doctor_id'] = doctor_instance
        if self.data.get('patient_data'):
            assert_error = self.create_patient_instance()
            if assert_error:
                return assert_error, 400
        data['patient_id'] = self.patient_instance.id
        data['timestamp'] = datetime.now()
        prescription_instance = prescription_model.Prescription(**data)
        db.session.add(prescription_instance)
        db.session.commit()
        treatment_list = self.data.get('treatment')
        for treatment in treatment_list:
            validation_error = field_validation.validate_fields(
                treatment, 'TREATMENT')
            if validation_error:
                return validation_error, 400
            treatment_data = {}
            treatment_data['prescription_id'] = prescription_instance.id
            treatment_data['medication'] = treatment.get('medication')
            treatment_instance = prescription_model.Treatment(**treatment_data)
            db.session.add(treatment_instance)
        diagnosis_list = self.data.get('diagnosis')
        for diagnosis in diagnosis_list:
            validation_error = field_validation.validate_fields(
                diagnosis, 'DIAGNOSIS')
            if validation_error:
                return validation_error, 400
            diagnosis_data = {}
            diagnosis_data['prescription_id'] = prescription_instance.id
            diagnosis_data['cause'] = diagnosis.get('cause')
            diagnosis_instance = prescription_model.Diagnosis(**diagnosis_data)
            db.session.add(diagnosis_instance)
        db.session.commit()
        return {'message': 'Prescription created successfully.'}, 200

    def create_patient_instance(self):
        data = self.data.get('patient_data')
        try:
            patient_user_instance = user_model.User.query.filter_by(
                username=data.get('phone_number')).first()
            patient_mapping_instance = user_model.UserMapping.query.filter_by(
                user_id=patient_user_instance.id).first()
            patient_instance = user_model.Patient.query.filter_by(
                id=patient_mapping_instance.entity_id).first()
            if patient_user_instance:
                self.patient_instance = patient_user_instance
                return
        except Exception:
            pass
        user_data, user_mapping_data, patient_data = {}, {}, {}
        validation_error = field_validation.validate_fields(
            data, 'PATIENT_INFO')
        if validation_error:
            return validation_error
        user_data['username'] = data.get('phone_number')
        full_name = data.get('patient_name')
        user_data.update(self.parse_full_name(full_name))
        user_instance = user_model.User(**user_data)
        patient_data['dob'] = parser.parse(data.get('dob'))
        patient_data['gender'] = data.get('patient_gender')
        patient_data['address'] = data.get('address', str())
        patient_instance = user_model.Patient(**patient_data)
        try:
            db.session.add(user_instance)
            db.session.add(patient_instance)
            db.session.commit()
            user_mapping_data['user_id'] = user_instance.id
            user_mapping_data['entity_id'] = patient_instance.id
            user_mapping8_data['entity_type'] = 'Patient'
            user_mapping_data['password'] = hashlib.sha256(data.get(
                'phone_number').encode('utf-8')).hexdigest()
            user_mapping_instance = user_model.UserMapping(**user_mapping_data)
            db.session.add(user_mapping_instance)
            db.session.commit()
            self.patient_instance = user_instance
        except:
            db.session.rollback()
            db.session.delete(patient_instance)
            db.session.commit()
            return {'error': 'User already exists'}

    def parse_full_name(self, full_name):
        data = {}
        if not full_name:
            return data
        full_name = full_name.split(' ')
        if len(full_name) >= 1:
            data['first_name'] = full_name[0]
        if len(full_name) == 3:
            data['middle_name'] = full_name[1]
        if len(full_name) >= 2:
            data['last_name'] = full_name[-1]
        return data

    def __call__(self):
        return self.write_prescription()


class GetPatientInfo(tools.Request):

    def __init__(self, request):
        super().__init__(request)

    def get_patient_info(self):
        data = {}
        user_id = self.args.get('user_id')
        try:
            user_instance = user_model.User.query.get(user_id)
            map_instance = user_model.UserMapping.query.filter_by(
                user_id=user_instance.id,
                entity_type='Patient').first()
            patient_instance = user_model.Patient.query.get(
                map_instance.entity_id)
        except Exception:
            return {'error': 'User not found'}, 400
        data['phone_number'] = user_instance.phone_number
        data['full_name'] = user_instance.full_name
        data['age'] = patient_instance.age
        data['address'] = patient_instance.address
        data['gender'] = patient_instance.gender
        return data, 200

    def __call__(self):
        return self.get_patient_info()
