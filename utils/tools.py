import json


class Request:

    def __init__(self, request):
        self.args = request.args
        self.headers = request.headers
        self.method = request.method
        self.data = json.loads(request.get_data().decode('utf-8'))