from collections import defaultdict
from prescription.models import *
from users.models import *
from utils import tools
from app import db


class GetPatientList(tools.Request):

    def __init__(self, request):
        super().__init__(request)

    def get_patient_list(self):
        data_type = self.args.get('data_type')
        if data_type not in ['patient', 'prescription']:
            return {'error': 'Please pass in proper data type.'}
        data = {}
        patient_dict = {}
        diagnosis_dict = defaultdict(list)
        doctor_id = self.args.get('doctor_id')
        prescription_instances = models.Prescription.query.filter_by(
            doctor_id=doctor_id)
        for prescription in prescription_instances:
            diagnosis_ids.append(prescription.id)
            patient_ids.append(prescription.patient_id)
        diagnosis_instances = models.Diagnosis.query.filter(
            Diagnosis.id.in_([prescriptions_ids]))
        patient_instances = models.Patient.query.filter(
            Patient.id.in_([patient_ids]))
        for field in diagnosis_instances:
            diagnosis_dict[field.prescription_id].append(field.cause)
        for field in patient_instances:
            full_name = str()
            if field.first_name:
                full_name += field.first_name
            if field.middle_name:
                full_name += field.middle_name
            if field.last_name:
                full_name += field.last_name
            patient_dict[field.id] = full_name
        for prescription in prescription_instances:
            fields = {}
            fields['patient_name'] = patient_dict.get(prescription.patient_id)
            if self.args.get('type') == 'patient':
                fields['timestamp'] = prescription.timestamp
            if self.args.get('type') == 'prescription':
                fields['prescription_id'] = prescription.id
            diagnosis = diagnosis_dict.get(prescription.id)
            fields['diagnosis'] = diagnosis
            data.append(fields)
        return data, 200

    def __call__(self):
        return self.get_patient_list()


class GetAllMedicine(tools.Request):
    def __init__(self, request):
        super().__init__(request)

    def get_all_medicine(self):
        result = []
        alphabet = self.args.get('alphabet')
        medicine_ids, medicine_tracker = [], {}
        user_id = self.args.get('user_id')
        in_stock_medicines = models.AvailableMedicine.query.filter_by(
            pharmacist_id=user_id)
        for medicine in in_stock_medicines:
            medicine_ids.append(medicine.medicine_id)
        medicines = models.Medicine.query.filter(
            Medicine.id.in_([medicine_ids]))
        for medicine in medicines:
            if medicine.title[0].lower() != alphabet.lower():
                continue
            data = {}
            data['title'] = medicine.title
            data['details'] = medicine.details
            medicine_tracker[medicine.id] = data
        for medicine in in_stock_medicines:
            required_data = {}
            required_data['title'] = medicine_tracker.get(
                medicine.medicine_id).get('title')
            required_data['details'] = medicine_tracker.get(
                medicine.medicine_id).get('details')
            result.append(required_data)
        return result, 200

    def __call__(self):
        return self.get_all_medicine()


class UpdateMedicine(tools.Request):

    def __init__(self, request):
        super().__init__(request)

    def update_medicine(self):
        validation_error = field_validation.validate_fields(
            self.data, 'UPDATE_MEDICINE')
        if validation_error:
            return validation_error, 400
        token = self.headers.get('Authorization')
        user_id = models.AuthToken.query.filter(
            token=token,
            user_type='Pharmacy').first().user_id
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

        medicine_instance = models.Medicine(id=medicine_id).first().id
        available_medicine_instance = models.AvailableMedicine(
            user_id=self.get_user_instance,
            medicine_id=medicine_instance)
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
        available_medicine_instance = models.AvailableMedicine(
            user_id=self.get_user_instance,
            medicine_id=medicine_instance)
        for medicine in available_medicine_instance:
            medicine_ids.append(medicine.prescription_id)
        medicine_instances = models.Diagnosis.query.filter(
            Medicine.id.in_(medicine_ids),
            Medicine.id.match(query))
        for medicine in medicine_instances:
            required_fields = {}
            required_fields['title'] = medicines.title
            required_fields['details'] = medicine
            data.append(required_fields)
        return data

    def __call__(self):
        return self.search_medicine()


class AddMedicine(tools.Request):

    def __init__(self):
        super().__init__(request)

    def add_medicine(self):
        data = {}
        data['in_stock'] = self.data.get('in_stock')
        data['medicine_id'] = self.data.get('medicine_id')
        data['user_id'] = self.get_user_instance
        available_medicine_instance = models.AvailableMedicine(**data)
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

        prescription_instance = Prescription.query.filter_by(
            id=prescription_id)
        patient_user_instance = User.query.filter_by(
            id=prescription_instance.patient_id)
        patient_map_instance = UserMapping.query.filter_by(
            user_id=patient_user_instance.id,
            entity_type='Patient')
        patient_instance = Patience.query.filter_by(
            id=patient_map_instance.entity_id)
        doctor_user_instance = User.query.filter_by(
            id=prescription_instance.doctor_id)
        doctors_map_instance = UserMapping.query.filter_by(
            id=doctor_user_instance.id,
            entity_type='Doctor')
        doctor_instance = Doctor.query.filter_by(
            id=doctors_map_instance.entity_id)
        diagnosis_instances = Diagnosis.query.filter_by(
            prescription_id=prescription_id)
        treatment_instances = Treatment.query.filter_by(
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
        data['doctor_id'] = doctor_instance.id
        if self.data.get('patient_data'):
            assert_error = self.create_patient_instance()
            if assert_error:
                return assert_error, 400
        if self.data.get('patient_id'):
            data['patient_id'] = self.data.get('patient_id')
        else:
            data['patient_id'] = self.patient_instance.id
        data['timestamp'] = datetime.now()
        prescription_instance = Prescription(**data)
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
            treatment_data['cause'] = treatment.get('cause')
            treatment_instance = Treatment(**treatment_data)
            db.session.add(treatment_instance)
        diagnosis_list = self.data.get('diagnosis')
        for diagnosis in diagnosis_list:
            validation_error = field_validation.validate_fields(
                diagnosis, 'DIAGNOSIS')
            if validation_error:
                return validation_error, 400
            diagnosis_data = {}
            diagnosis_data['prescription_id'] = prescription_instance.id
            diagnosis_data['diagnosis'] = diagnosis.get('diagnosis')
            diagnosis_instance = Diagnosis(**diagnosis_data)
            db.session.add(diagnosis_instance)
        db.session.commit()
        return {'message': 'Prescription created successfully.'}, 400

    def create_patient_instance(self):
        data = {}
        user_data, user_mapping_data, patient_data = {}, {}, {}
        patient_data = self.data.get('patient_data')
        validation_error = field_validation.validate_fields(
            patient_data, 'PATIENT_INFO')
        if validation_error:
            return validation_error
        user_data['username'] = patient_data.get('phone_number')
        full_name = patient_data.get('patient_name')
        user_data.update(self.parse_full_name(full_name))
        user_data['password'] = hashlib.sha256(patient_data.get(
            'phone_number').encode('utf-8')).hexdigest()
        user_instance = User(**user_data)
        patient_data['dob'] = parser.parse(patient_data.get('patient_age'))
        patient_data['gender'] = patient_data.get('patient_gender')
        patient_data['address'] = patient_data.get('address', str())
        patient_instance = Patient(**patient_data)
        db.session.add(patient_instance)
        db.session.commit()
        data['user_id'] = user_instance.id
        data['entity_id'] = patient_instance.id
        data['entity_type'] = 'Patient'
        UserMapping(**data)
        self.patient_instance = user_instance

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
        super().__init__(self)

    def get_patient_info():
        data = {}
        username = self.args.get('user_id')
        try:
            user_instance = User.query.filter_by(username=username)
            map_instance = UserMapping.query.filter_by(
                user_id=user_instance.id,
                entity_type='Patient')
            patient_instance = Patient.query.filter_by(
                id=map_instance.entity_id)
        except Exception:
            return {'error': 'User not found'}, 400
        data['phone_number'] = user_instance.username
        data['first_name'] = user_instance.first_name
        data['middle_name'] = user_instance.middle_name
        data['last_name'] = user_instance.last_name
        data['age'] = patient_instance.age
        data['address'] = patient_instance.address
        data['gender'] = patient_instance.gender
        return data, 200

    def __call__():
        return self.get_patient_info()
