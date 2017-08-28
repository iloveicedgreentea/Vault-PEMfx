"""
This is just a module for Vault communication

"""

import json
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# Useful when testing with untrusted certs. Disable in production


class VaultCom:
    def __init__(self, url, token, subdir):
        self.put_secret = '/v1/secret/'
        self.unseal_status = '/v1/sys/health'
        self.url = url
        self.token = token
        self.subdir = subdir

    def call_api(self, method, api, jsondata=None):
        api_url = f'{self.url}{api}'
        headers = {"X-Vault-Token": f'{self.token}'}

        if method.lower() == 'put':
            response = requests.put(api_url, headers=headers, data=jsondata, verify=False)
        elif method.lower() == 'post':
            response = requests.post(api_url, headers=headers, data=jsondata, verify=False)
        elif method.lower() == 'delete':
            response = requests.delete(api_url, headers=headers, data=jsondata, verify=False)
        else:
            response = requests.get(api_url, headers=headers, verify=False)

        if response.status_code is None:
            raise Exception(f'Connection error with {api} : {requests.ConnectionError}')
        try:
            return response.json()
        except ValueError as e:
            if response.status_code == 204:
                pass  # we pass because some API calls return a 204 which is fine, otherwise requests gets mad
            else:
                print(e)

    def get_vault_status(self):
        return self.call_api(method='get', api=self.unseal_status)

    def put_vault_secret(self, secret_name, secret_value):
        api_call = f'{self.put_secret}{self.subdir}/{secret_name}'
        apidata = json.dumps({f"{secret_name}": f"{secret_value}"})
        print(f'Uploading {secret_name} to {api_call}')
        return self.call_api(method='post', api=api_call, jsondata=apidata)




