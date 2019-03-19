import requests
import json
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

username = "smc"
password = "smc"
url = "https://172.21.25.210:8443/univmax/restapi/sloprovisioning/symmetrix/000197700501/srp/SRP_1"
headers = {'content-type': 'application/json', 
            'accept': 'application/json'}
veryfySSL=False

session = requests.session()
session.headers = headers
session.auth = HTTPBasicAuth(username, password)
session.verify = veryfySSL

response = session.request('GET', url=url, timeout=60)
data = response.json()['srp'][0]

print(data)
print(data['total_usable_cap_gb'])