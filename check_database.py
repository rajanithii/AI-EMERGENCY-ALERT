import sqlite3
import json

# Connect to database
conn = sqlite3.connect(r'D:\newalert\lifeline.db')
conn.row_factory = sqlite3.Row  # Get results as dictionaries
c = conn.cursor()

print("=" * 80)
print("DATABASE CHECK - Emergency Alerts")
print("=" * 80)

# Get all emergencies
c.execute('SELECT * FROM emergencies ORDER BY id DESC LIMIT 10')
alerts = c.fetchall()

print(f"\nTotal emergencies (showing last 10):\n")

target_lat = 10.929426866666667
target_lon = 78.7374494

for alert in alerts:
    lat = alert['latitude']
    lon = alert['longitude']
    
    print(f"ID: {alert['id']}")
    print(f"  User: {alert['user_name']}")
    print(f"  Latitude: {lat} (type: {type(lat).__name__})")
    print(f"  Longitude: {lon} (type: {type(lon).__name__})")
    print(f"  Nearest Hospital: {alert['nearest_hospital']}")
    print(f"  Hospital Distance: {alert['hospital_distance']}")
    print(f"  Timestamp: {alert['timestamp']}")
    
    # Check if matches target coordinates
    if lat and lon:
        try:
            lat_float = float(lat)
            lon_float = float(lon)
            if abs(lat_float - target_lat) < 0.0001 and abs(lon_float - target_lon) < 0.0001:
                print(f"  ✓ MATCHES TARGET LOCATION")
        except:
            pass
    print()

# Find records with your exact coordinates
print("\n" + "=" * 80)
print(f"RECORDS WITH COORDINATES {target_lat}, {target_lon}")
print("=" * 80 + "\n")

c.execute('''
    SELECT * FROM emergencies 
    WHERE latitude = ? AND longitude = ?
    ORDER BY id DESC
''', (str(target_lat), str(target_lon)))

matching = c.fetchall()
print(f"Found {len(matching)} matching records:\n")

for alert in matching:
    print(f"ID: {alert['id']}")
    print(f"  User: {alert['user_name']}")
    print(f"  Coords: {alert['latitude']}, {alert['longitude']}")
    print(f"  Hospital: {alert['nearest_hospital']} ({alert['hospital_distance']}km)")
    print(f"  Time: {alert['timestamp']}")
    print()

# Show users table with location data
print("\n" + "=" * 80)
print("USERS - Last Location Data")
print("=" * 80 + "\n")

c.execute('SELECT id, name, last_latitude, last_longitude FROM users LIMIT 5')
users = c.fetchall()

for user in users:
    print(f"User ID: {user['id']} - {user['name']}")
    print(f"  Last Latitude: {user['last_latitude']}")
    print(f"  Last Longitude: {user['last_longitude']}")
    print()

conn.close()

print("\n✓ Database check complete!")
