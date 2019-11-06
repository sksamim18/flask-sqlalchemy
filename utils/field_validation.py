validation = {}

validation['PATIENT_REGISTRATION'] = {
    'type': str,
    'full_name': str,
    'phone_number': str,
    'password': str
}
validation['PHARMACY_REGISTRATION'] = {
    'type': str,
    'full_name': str,
    'phone_number': str,
    'password': str,
    'cerification': str,
    'work_ex': int
}
validation['DOCTOR_REGISTRATION'] = {
    'type': str,
    'full_name': str,
    'phone_number': str,
    'password': str,
    'qualification': str,
    'work_ex': int
}
validation['LOGIN'] = {
    'phone_number': str,
    'password': str,
    'type': str
}
validation['UPDATE_USER_PATIENT'] = {
    'dob': str,
    'address': str,
    'gender': str
}
validation['UPDATE_USER_DOCTOR'] = {
    'type': str,
    'nickname': str,
    'qualification': str,
    'work_ex': int,
    'address': str,
    'account_status': str
}
validation['UPDATE_USER_PHARMACY'] = {
    'type': str,
    'shop_name': str,
    'cerification': str,
    'work_ex': str,
    'opening_time': str,
    'closing_time': str,
    'address': str,
    'account_status': str,
    'user_id': str
}
validation['UPDATE_MEDICINE'] = {
    'medicine_id': int,
    'in_stock': int
}
validation['PATIENT_INFO'] = {
    'patient_name': str,
    'phone_number': str,
    'dob': str,
    'patient_gender': str
}
validation['TREATMENT'] = {
    'medication': str
}
validation['DIAGNOSIS'] = {
    'cause': str
}


def validate_update_fields(data, field_type):
    error_data = {}
    validation_mapping = validation.get(field_type)
    for field, value in data.items():
        required_type = validation_mapping.get(field)
        if required_type:
            if required_type != type(field):
                error_data[field] = "Please pass a {} data type".format(
                    required_type)
    return error_data


def validate_fields(data, field_type):
    error_data = {}
    required_fields = validation.get(field_type)
    for field, value in required_fields.items():
        if not data.get(field) or not isinstance(data.get(field), value):
            error_data[field] = 'Value missing or wrong type passed.'
    return error_data
