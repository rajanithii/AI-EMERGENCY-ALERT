#!/usr/bin/env python
"""Clean up all alerts from the database."""

from newalert.backend.database import SessionLocal, Emergency

def clear_all_alerts():
    db = SessionLocal()
    try:
        # Delete all emergency alerts
        count = db.query(Emergency).delete()
        db.commit()
        print(f"✅ Deleted {count} alerts from the database.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error deleting alerts: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🗑️ Clearing all alerts from the database...")
    clear_all_alerts()
