"""
Diagnostic script to check alert system issues
"""
import os
import sys
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from newalert.backend.database import SessionLocal, Emergency, User
from sqlalchemy import text

db = SessionLocal()

print("=" * 60)
print("ALERT DIAGNOSTICS")
print("=" * 60)

# 1. Check database exists
db_path = os.path.join(os.path.dirname(__file__), "lifeline.db")
print(f"\n✓ Database path: {db_path}")
print(f"  Exists: {os.path.exists(db_path)}")

# 2. Check Emergency table
print("\n" + "=" * 60)
print("EMERGENCY TABLE CONTENTS:")
print("=" * 60)
try:
    emergencies = db.query(Emergency).all()
    print(f"Total emergencies in database: {len(emergencies)}\n")
    
    if emergencies:
        for e in emergencies:
            print(f"ID: {e.id}")
            print(f"  User ID: {e.user_id}")
            print(f"  User Name: {e.user_name}")
            print(f"  Status: {e.status}")
            print(f"  Timestamp: {e.timestamp}")
            print(f"  Location: ({e.latitude}, {e.longitude})")
            print(f"  Hospital: {e.nearest_hospital} ({e.hospital_distance}km)")
            print()
    else:
        print("⚠ NO EMERGENCIES FOUND IN DATABASE")
        print("  - Alerts may not be being created")
        print("  - Check if sendEmergencyAlert() is being called")
        
except Exception as e:
    print(f"❌ Error querying emergencies: {e}")

# 3. Check Users
print("=" * 60)
print("USERS IN DATABASE:")
print("=" * 60)
try:
    users = db.query(User).all()
    print(f"Total users: {len(users)}\n")
    for u in users:
        print(f"ID: {u.id} | Name: {u.name} | Email: {u.email} | Role: {u.role}")
        print(f"  Last Location: ({u.last_latitude}, {u.last_longitude})")
except Exception as e:
    print(f"❌ Error querying users: {e}")

# 4. Check API endpoint directly
print("\n" + "=" * 60)
print("API ENDPOINT TEST:")
print("=" * 60)

import requests
try:
    response = requests.get('http://localhost:8000/api/emergencies', timeout=5)
    print(f"GET /api/emergencies")
    print(f"  Status: {response.status_code}")
    data = response.json()
    print(f"  Response: {len(data) if isinstance(data, list) else 'error'} items")
    print(f"  Data: {data}")
except Exception as e:
    print(f"❌ Cannot reach API: {e}")
    print("  - Make sure FastAPI is running on port 8000")
    print("  - Run: python -m newalert.backend.main (or uvicorn newalert.backend.main:app --reload)")

# 5. Check 24-hour cutoff
print("\n" + "=" * 60)
print("ALERT AGE CHECK:")
print("=" * 60)
now = datetime.utcnow()
cutoff = now - timedelta(hours=24)
print(f"Current time (UTC): {now.isoformat()}")
print(f"24-hour cutoff:     {cutoff.isoformat()}")
print(f"Alerts created after {cutoff} will appear on dashboard")

try:
    fresh_alerts = []
    stale_alerts = []
    
    for e in db.query(Emergency).all():
        try:
            ts = datetime.fromisoformat(e.timestamp)
            if ts >= cutoff:
                fresh_alerts.append(e)
            else:
                stale_alerts.append(e)
        except:
            pass
    
    print(f"\nFresh alerts (< 24h):  {len(fresh_alerts)}")
    print(f"Stale alerts (> 24h):  {len(stale_alerts)}")
    
except Exception as e:
    print(f"❌ Error: {e}")

db.close()

print("\n" + "=" * 60)
print("DEBUGGING TIPS:")
print("=" * 60)
print("1. If NO EMERGENCIES found:")
print("   - Check browser console for errors when clicking SOS button")
print("   - Verify user is logged in before trying to send alert")
print("   - Ensure geolocation permission is granted")
print()
print("2. If emergencies exist but not showing on dashboard:")
print("   - Check if status is 'new' (should be)")
print("   - Check if timestamp is within 24 hours")
print("   - Check hospital browser console for fetch errors")
print()
print("3. To test manually:")
print("   - Run: python add_users.py (to add test user)")
print("   - Then POST to /api/emergency/alert:")
print("     curl -X POST http://localhost:8000/api/emergency/alert \\")
print("       -H 'Content-Type: application/json' \\")
print("       -d '{\"user_id\": 1, \"latitude\": \"10.7905\", \"longitude\": \"78.7047\"}'")
print("=" * 60)
