import requests
import json
import time

# Create emergency alert with the user's exact coordinates
payload = {
    'user_id': 1,
    'latitude': '10.929426866666667',
    'longitude': '78.7374494'
}

url = 'http://182.18.2.8:8000/api/emergency/alert'
print("Sending emergency alert with coordinates:")
print(f"  Latitude: {payload['latitude']}")
print(f"  Longitude: {payload['longitude']}")

try:
    r = requests.post(url, json=payload, timeout=5)
    print(f"\nAlert creation status: {r.status_code}")
    print(f"Response: {r.text}")
except Exception as e:
    print(f"ERROR creating alert: {e}")
    exit(1)

# Wait for backend to process
time.sleep(1)

# Fetch emergencies to verify coordinates were stored
try:
    r = requests.get('http://182.18.2.8:8000/api/emergencies', timeout=5)
    emergencies = r.json()
    
    print(f"\nTotal emergencies: {len(emergencies)}")
    
    if emergencies:
        latest = emergencies[0]
        print("\nLatest emergency stored in DB:")
        print(f"  User: {latest.get('user_name')}")
        print(f"  Latitude (DB): {latest.get('latitude')}")
        print(f"  Longitude (DB): {latest.get('longitude')}")
        print(f"  Type: lat={type(latest.get('latitude')).__name__}, lon={type(latest.get('longitude')).__name__}")
        
        # Test parsing as float
        try:
            lat_float = float(latest.get('latitude'))
            lon_float = float(latest.get('longitude'))
            print(f"\n✓ Successfully parsed as floats:")
            print(f"  Latitude: {lat_float}")
            print(f"  Longitude: {lon_float}")
        except Exception as e:
            print(f"\n✗ Failed to parse as floats: {e}")
    else:
        print("No emergencies found")
        
except Exception as e:
    print(f"ERROR fetching emergencies: {e}")
    exit(1)
