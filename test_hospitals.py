import requests
url = 'http://182.18.2.8:8000/api/hospitals/nearby?lat=10.929300455873966&lon=78.7386510296276'
print('GET', url)
try:
    r = requests.get(url, timeout=10)
    print('Status:', r.status_code)
    print(r.text)
except Exception as e:
    print('Error:', e)
