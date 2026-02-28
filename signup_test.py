import requests

payload={
    'name':'NoCoords',
    'email':'nocoord@example.com',
    'password':'pass123',
    'role':'user',
    'phone':'1112223333'
}
res=requests.post('http://182.18.2.8:8000/api/signup',json=payload)
print(res.status_code, res.text)
