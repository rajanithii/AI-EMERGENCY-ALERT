import requests

print('sending alert')
res = requests.post('http://127.0.0.1:8000/api/emergency/alert', json={'user_id':1, 'latitude':'12.34', 'longitude':'56.78'})
print(res.status_code, res.text)
print('list alerts: (localhost)')
res2 = requests.get('http://127.0.0.1:8000/api/emergencies')
print(res2.status_code, res2.text)
