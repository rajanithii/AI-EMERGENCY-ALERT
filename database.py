import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

# ensure a single database file in workspace root
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATABASE_PATH = os.path.join(BASE_DIR, "lifeline.db")
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"  # absolute path to avoid duplicates

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

Base = declarative_base()


# ----------------------
# User Table
# ----------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    # additional emergency profile fields
    phone = Column(String, nullable=True)
    blood = Column(String, nullable=True)
    address = Column(String, nullable=True)
    is_verified = Column(Integer, default=0)   # 0 = Not verified, 1 = Verified
    otp = Column(String, nullable=True)
    # device location stored for user (last known)
    last_latitude = Column(String, nullable=True)
    last_longitude = Column(String, nullable=True)
    # timestamp fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


# ----------------------
# Emergency Alert Table
# ----------------------
class Emergency(Base):
    __tablename__ = "emergencies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    # User Personal Details
    user_name = Column(String, nullable=True)
    user_email = Column(String, nullable=True)
    user_password = Column(String, nullable=True)
    user_role = Column(String, nullable=True)
    # Location Data
    latitude = Column(String, nullable=True)
    longitude = Column(String, nullable=True)
    status = Column(String, default="new")
    timestamp = Column(String, nullable=False)
    nearest_hospital = Column(String, nullable=True)
    hospital_distance = Column(String, nullable=True)
    ai_recommendation = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


# ----------------------
# Create Tables
# ----------------------
def init_db():
    # create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    # sqlite won't autoupdate existing tables, so try adding new columns
    # ignore errors if column already present
    with engine.connect() as conn:
        for coldef in ("phone TEXT", "blood TEXT", "address TEXT"):
            try:
                conn.execute(f"ALTER TABLE users ADD COLUMN {coldef}")
            except Exception:
                pass

        # add location columns for storing latest known coordinates from user's device
        for coldef in ("last_latitude TEXT", "last_longitude TEXT"):
            try:
                conn.execute(f"ALTER TABLE users ADD COLUMN {coldef}")
            except Exception:
                pass

        # add datetime columns to users table
        for coldef in ("created_at DATETIME", "updated_at DATETIME"):
            try:
                conn.execute(f"ALTER TABLE users ADD COLUMN {coldef}")
            except Exception:
                pass

        # AI recommendation field for emergencies
        try:
            conn.execute('ALTER TABLE emergencies ADD COLUMN ai_recommendation TEXT')
        except Exception:
            pass

        # add datetime columns to emergencies table
        for coldef in ("alert_timestamp DATETIME", "created_at DATETIME"):
            try:
                conn.execute(f"ALTER TABLE emergencies ADD COLUMN {coldef}")
            except Exception:
                pass


# ----------------------
# DB Dependency (VERY IMPORTANT)
# ----------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()