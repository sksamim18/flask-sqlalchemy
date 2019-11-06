import json
from functools import wraps
from flask import request

from users import models


class Request:

    def __init__(self, request):
        self.args = request.args
        self.headers = request.headers
        self.method = request.method
        if self.method == 'POST':
            self.data = json.loads(request.get_data().decode('utf-8'))

    @property
    def get_user_instance(self):
        token = self.headers.get('Authorization')
        user_id = models.AuthToken.query.filter_by(
            token=token).first().user_id
        return user_id


def login_required_doctor(f):
    @wraps(f)
    def verify_user(*args, **kwargs):
        auth_token = request.headers.get('Authorization', str())
        login_type = 'Doctor'
        auth_instance = models.AuthToken.query.filter_by(
            user_type=login_type,
            token=auth_token).first()
        if not auth_instance:
            return {'error': "Page not avaiabale"}, 401
        return f(*args, **kwargs)
    return verify_user


def login_required_pharmacist(f):
    @wraps(f)
    def verify_user(*args, **kwargs):
        auth_token = request.headers.get('Authorization', str())
        login_type = 'Pharmacist'
        auth_instance = models.AuthToken.query.filter_by(
            user_type=login_type,
            token=auth_token).first()
        if not auth_instance:
            return {'error': "Page not avaiabale"}, 401
        return f(*args, **kwargs)
    return verify_user


def login_required(f):
    @wraps(f)
    def verify_user(*args, **kwargs):
        auth_token = request.headers.get('Authorization', str())
        auth_instance = models.AuthToken.query.filter_by(
            token=auth_token).first()
        if not auth_instance:
            return {'error': 'Page not avaialable'}, 401
        return f(*args, **kwargs)
    return verify_user
