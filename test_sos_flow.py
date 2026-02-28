#!/usr/bin/env python3
import requests
import json

BASE_URL = 'http://10.226.149.195:8000/api'

print("=" * 60)
print("Testing SOS Alert Flow")
print("=" * 60)

# 1. Create test user
print("\n1. Creating test user...")
signup_data = {
    'name': 'Test User',
    'email': 'testuser@example.com',
    'password': 'test123',
    'role': 'user',
    'phone': '+1234567890',
    'blood': 'O+',
    'address': '123 Test St'
}
r = requests.post(f'{BASE_URL}/signup', json=signup_data)
print(f"   Status: {r.status_code}")
print(f"   Response JSON: {r.json()}")
user_id = r.json().get('user_id', 1)
print(f"   User ID: {user_id}")
# fetch the stored profile and display to verify
r2 = requests.get(f'{BASE_URL}/user/{user_id}')
print(f"   Stored profile: {r2.json()}")

# 2. Send SOS alert with location
print("\n2. Sending SOS alert with GPS coordinates...")
alert_data = {
    'user_id': user_id,
    'latitude': '40.7128',  # NYC latitude
    'longitude': '-74.0060'  # NYC longitude
}
r = requests.post(f'{BASE_URL}/emergency/alert', json=alert_data)
print(f"   Status: {r.status_code}")
print(f"   Response: {r.text}")

# 3. Fetch all emergencies (what hospital dashboard sees)
print("\n3. Fetching emergencies list (Hospital Dashboard)...")
r = requests.get(f'{BASE_URL}/emergencies')
print(f"   Status: {r.status_code}")
emergencies = r.json()
print(f"   Total alerts: {len(emergencies)}")
if emergencies:
    for alert in emergencies:
        print(f"\n   Alert #{alert['id']}:")
        print(f"     User ID: {alert['user_id']}")
        print(f"     Lat/Lon: {alert['latitude']}/{alert['longitude']}")
        print(f"     Nearest Hospital: {alert.get('nearest_hospital', 'N/A')}")
        print(f"     Distance: {alert.get('hospital_distance', 'N/A')} km")
        print(f"     Timestamp: {alert['timestamp']}")
else:
    print("   ❌ NO ALERTS FOUND!")

print("\n" + "=" * 60)
print("Test complete - check hospital dashboard at:")
print("http://10.226.149.195:8001/hospital-home.html")
print("=" * 60)
