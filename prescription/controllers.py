from collections import defaultdict
from prescription import models
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
        available_medicine_instance.in_stock = (
            available_medicine_instance.in_stock - sold_unit)

        if available_medicine_instance < 0:
            return {'error': 'Quantity unavailable'}, 400

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
        available_medicine_instance = AvailableMedicine(**data)
        db.session.add(available_medicine_instance)
        db.session.commit()
        return {'message': 'Medicine updated successfully.'}, 201

    def __call__(self):
        return self.add_medicine()
