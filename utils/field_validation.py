validation = {}

validation['PATIENT_REGISTRATION'] = {
    'full_name': str,
    'phone_number': str,
    'password': str
}
validation['PHARMACY_REGISTRATION'] = {
    'full_name': str,
    'phone_number': str,
    'password': str,
    'cerification': str,
    'work_ex': int
}
validation['DOCTOR_REGISTRATION'] = {
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


def validate_fields(data, field_type):
    error_data = {}
    required_fields = validation.get(field_type)
    for field, value in required_fields.items():
        if not data.get(field) or not isinstance(data.get(field), value):
            error_data[field] = 'Value missing or wrong type passed.'
    return error_data
