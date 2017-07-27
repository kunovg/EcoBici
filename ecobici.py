import time
import requests

class EcobiciManager():
    def __init__(self, client_secret, client_id):
        self.client_secret = client_secret
        self.client_id = client_id
        self.access_token = None
        self.expires_in = None
        self.refresh_token = None
        self.token_type = None
        self.token_created = None
        self.get_access_token()

    def get_access_token(self):
        url = 'https://pubsbapi.smartbike.com/oauth/v2/token?client_id={}&client_secret={}&grant_type=client_credentials'.format(self.client_id, self.client_secret)
        r = requests.get(url)
        self.access_token = r.json().get('access_token')
        self.expires_in = r.json().get('expires_in')
        self.refresh_token = r.json().get('refresh_token')
        self.token_type = r.json().get('token_type')
        self.token_created = time.time()
        print('Access Token definido correctamente')

    def refresh_token(self):
        url = 'https://pubsbapi.smartbike.com/oauth/v2/token?client_id={}&client_secret={}&grant_type=refresh_token&refresh_token={}'.format(self.client_id, self.client_secret, self.refresh_token)
        r = requests.get(url)
        self.access_token = r.json().get('access_token')
        self.expires_in = r.json().get('expires_in')
        self.refresh_token = r.json().get('refresh_token')
        self.token_type = r.json().get('token_type')
        self.token_created = time.time()

    def token_validation(self):
        if (time.time() - self.token_created) > self.expires_in:
            self.refresh_token()

    def get_stations(self):
        self.token_validation()
        url = 'https://pubsbapi.smartbike.com/api/v1/stations.json?access_token={}'.format(self.access_token)
        r = requests.get(url)
        return r.json()['stations']

    def get_available(self):
        self.token_validation()
        url = 'https://pubsbapi.smartbike.com/api/v1/stations/status.json?access_token={}'.format(self.access_token)
        r = requests.get(url)
        return r.json()['stationsStatus']
