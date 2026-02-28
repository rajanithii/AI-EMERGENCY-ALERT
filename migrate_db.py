import sqlite3

# Create proper database migration
conn = sqlite3.connect(r'D:\newalert\lifeline.db')
c = conn.cursor()

print("Running database migration...\n")

# Check and add missing columns to users table
try:
    c.execute('PRAGMA table_info(users)')
    columns = {row[1] for row in c.fetchall()}
    
    if 'last_latitude' not in columns:
        print("Adding last_latitude column to users...")
        c.execute('ALTER TABLE users ADD COLUMN last_latitude TEXT')
        conn.commit()
        print("✓ Added last_latitude\n")
    else:
        print("✓ last_latitude already exists\n")
    
    if 'last_longitude' not in columns:
        print("Adding last_longitude column to users...")
        c.execute('ALTER TABLE users ADD COLUMN last_longitude TEXT')
        conn.commit()
        print("✓ Added last_longitude\n")
    else:
        print("✓ last_longitude already exists\n")
        
except Exception as e:
    print(f"Error adding columns: {e}\n")

# Now check the database structure
print("=" * 80)
print("USERS TABLE STRUCTURE")
print("=" * 80 + "\n")

c.execute('PRAGMA table_info(users)')
columns = c.fetchall()
for col in columns:
    print(f"  {col[1]}: {col[2]}")

print("\n" + "=" * 80)
print("EMERGENCIES TABLE STRUCTURE")
print("=" * 80 + "\n")

c.execute('PRAGMA table_info(emergencies)')
columns = c.fetchall()
for col in columns:
    print(f"  {col[1]}: {col[2]}")

print("\n" + "=" * 80)
print("DATABASE SAMPLE DATA")
print("=" * 80 + "\n")

# Check users with coordinates
c.execute('SELECT id, name, last_latitude, last_longitude FROM users')
users = c.fetchall()
print(f"Users with location data:\n")
for user in users:
    print(f"  User {user[0]} ({user[1]}): {user[2]}, {user[3]}")

print(f"\nTotal users: {len(users)}")

# Check emergencies with coordinates
c.execute('SELECT COUNT(*) FROM emergencies WHERE latitude IS NOT NULL AND longitude IS NOT NULL')
count_with_coords = c.fetchone()[0]

c.execute('SELECT COUNT(*) FROM emergencies')
total_count = c.fetchone()[0]

print(f"\nEmergencies with coordinates: {count_with_coords}/{total_count}")

# Check which ones have nearest hospital
c.execute('SELECT COUNT(*) FROM emergencies WHERE nearest_hospital IS NOT NULL')
count_with_hospital = c.fetchone()[0]

print(f"Emergencies with nearest hospital: {count_with_hospital}/{total_count}")

conn.close()

print("\n✓ Migration complete!")
