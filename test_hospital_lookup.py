import requests
import time
import sqlite3

print("Testing emergency alert with hospital lookup...\n")

# Create emergency with your coordinates
payload = {
    'user_id': 1,
    'latitude': '10.929426866666667',
    'longitude': '78.7374494'
}

url = 'http://182.18.2.8:8000/api/emergency/alert'
print(f"1. Creating emergency alert...")
print(f"   URL: {url}")
print(f"   Latitude: {payload['latitude']}")
print(f"   Longitude: {payload['longitude']}\n")

try:
    r = requests.post(url, json=payload, timeout=5)
    print(f"   Response: {r.status_code} - {r.text}\n")
except Exception as e:
    print(f"   ERROR: {e}\n")
    exit(1)

# Wait for background task to complete
print("2. Waiting 3 seconds for background hospital lookup task to complete...\n")
time.sleep(3)

# Check if hospital was populated
print("3. Checking database for hospital data...\n")

conn = sqlite3.connect(r'D:\newalert\lifeline.db')
c = conn.cursor()

# Get the latest alert
c.execute('''
    SELECT id, latitude, longitude, nearest_hospital, hospital_distance 
    FROM emergencies 
    WHERE latitude = ? AND longitude = ?
    ORDER BY id DESC LIMIT 1
''', ('10.929426866666667', '78.7374494'))

result = c.fetchone()

if result:
    alert_id, lat, lon, hospital, distance = result
    print(f"   Alert ID: {alert_id}")
    print(f"   Coordinates: {lat}, {lon}")
    print(f"   Nearest Hospital: {hospital}")
    print(f"   Distance: {distance}km")
    
    if hospital:
        print(f"\n✓ SUCCESS! Hospital lookup is working!")
        print(f"  Found nearby hospital: {hospital} ({distance}km away)")
    else:
        print(f"\n✗ Hospital lookup not completed yet or failed")
        print(f"  Check server logs and try again in a few seconds")
else:
    print("✗ No alert found in database")

conn.close()

# Also show what hospitals should be available
print("\n4. Available hospitals for your location:\n")
try:
    r = requests.get(
        'http://182.18.2.8:8000/api/hospitals/nearby?lat=10.929426866666667&lon=78.7374494',
        timeout=10
    )
    hospitals = r.json()
    print(f"   Found {len(hospitals)} hospitals nearby:\n")
    for i, h in enumerate(hospitals[:5], 1):
        print(f"   {i}. {h['name']}")
        print(f"      Distance: {h['distance']} km")
except Exception as e:
    print(f"   ERROR fetching hospitals: {e}")
