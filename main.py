from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from newalert.backend.database import SessionLocal, init_db, User, Emergency
from newalert.backend.auth import hash_password, verify_password, get_user_by_email, generate_otp
from newalert.backend.email_service import send_otp_email
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
from typing import Optional
import os
import math
import requests
from newalert.backend import location_service


app = FastAPI(title="LifeLine API", version="1.0.0")

# ============ INIT DB ============
init_db()

# ============ PATH SETUP ============
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")

# Load environment variables (including Hugging Face token) from .env if available
env_path = os.path.join(BASE_DIR, '.env')
try:
    from dotenv import load_dotenv
    load_dotenv(env_path)
except Exception:
    # python-dotenv not installed; attempt a minimal manual parse of .env
    try:
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for ln in f:
                    ln = ln.strip()
                    if not ln or ln.startswith('#') or '=' not in ln:
                        continue
                    k, v = ln.split('=', 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    if k and v and os.getenv(k) is None:
                        os.environ[k] = v
    except Exception:
        pass

# expose a flag indicating whether the Hugging Face token is present (do NOT log the token itself)
HUGGING_FACE_TOKEN = os.getenv('HUGGING_FACE_TOKEN')
HUGGING_FACE_TOKEN_LOADED = bool(HUGGING_FACE_TOKEN)
print('HUGGING_FACE_TOKEN loaded:', HUGGING_FACE_TOKEN_LOADED)

# ============ STATIC ============
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# ============ CORS ============
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ DATABASE DEPENDENCY ============
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============ MODELS ============
class SignupModel(BaseModel):
    name: str
    email: str
    password: str
    role: str
    # additional emergency profile fields collected at registration
    phone: Optional[str] = None
    blood: Optional[str] = None
    address: Optional[str] = None
    # device coordinates at time of signup (optional)
    latitude: Optional[str] = None
    longitude: Optional[str] = None

class LoginModel(BaseModel):
    email: str
    password: str

class OTPVerifyModel(BaseModel):
    email: str
    otp: str

class UserProfileModel(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    # allow editing emergency profile fields
    phone: Optional[str] = None
    blood: Optional[str] = None
    address: Optional[str] = None

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

# ============ FRONTEND ROUTES ============
@app.get("/")
def serve_login():
    return FileResponse(os.path.join(FRONTEND_DIR, "login-connected.html"))

@app.get("/signup.html")
def signup_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "signup.html"))

@app.get("/role-select.html")
def role_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "role-select.html"))

@app.get("/user.html")
def user_page():
    # serve the patient dashboard directly using the existing
    # `user.html` file. older code redirected here to a non-existent
    # `home.html`, which caused front-end navigation failures.
    return FileResponse(os.path.join(FRONTEND_DIR, "user.html"))

@app.get("/profile-view.html")
def profile_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "profile-view.html"))

@app.get("/hospital-home.html")
def hospital_home_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "hospital-home.html"))

@app.get("/hospital-profile.html")
def hospital_profile_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "hospital-profile.html"))

@app.get("/login-connected.html")
def login_connected_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "login-connected.html"))

# ============ AUTH ============
@app.post("/api/signup")
def signup(data: SignupModel, db: Session = Depends(get_db)):
    existing_user = get_user_by_email(db, data.email)

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        # ✅ HASH PASSWORD
        hashed_pwd = hash_password(data.password)
        
        # ✅ CREATE USER - include optional profile fields only for regular users
        # receivers don't need personal profile data
        # ensure we always have some coordinate values; use predefined default when the
        # client didn't provide a location (e.g. user denied geolocation).
        default_lat = "10.7905"  # Tiruchirappalli, Tamil Nadu
        default_lon = "78.7047"  # Tiruchirappalli, Tamil Nadu
        lat_val = data.latitude if data.latitude is not None else default_lat
        lon_val = data.longitude if data.longitude is not None else default_lon

        user_kwargs = {
            'name': data.name,
            'email': data.email,
            'password': hashed_pwd,
            'role': data.role,
            'otp': None,
            'is_verified': 1,
            # store initial device coordinates (default if missing)
            'last_latitude': lat_val,
            'last_longitude': lon_val,
        }
        if data.role == 'user':
            user_kwargs.update({
                'phone': data.phone,
                'blood': data.blood,
                'address': data.address,
            })
        else:
            user_kwargs.update({'phone': None, 'blood': None, 'address': None})

        new_user = User(**user_kwargs)

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {
            "message": "✅ Account created successfully! You can now login.",
            "email": data.email,
            "user_id": new_user.id,
            "profile": {
                "phone": new_user.phone,
                "blood": new_user.blood,
                "address": new_user.address,
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")

@app.post("/api/verify-otp")
def verify_otp(data: OTPVerifyModel, db: Session = Depends(get_db)):
    user = get_user_by_email(db, data.email)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.otp != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    user.is_verified = 1
    user.otp = None
    db.commit()

    return {"message": "Email verified successfully!", "user_id": user.id}

@app.post("/api/login")
def login(data: LoginModel, db: Session = Depends(get_db)):
    user = get_user_by_email(db, data.email)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Verify OTP first")

    if not verify_password(data.password, user.password):
        raise HTTPException(status_code=400, detail="Wrong password")

    # return basic profile so frontend can show emergency info directly
    user_data = {
        "id": user.id,
        "role": user.role,
        "name": user.name,
        "email": user.email,
    }
    if user.role == 'user':
        user_data.update({
            "phone": user.phone,
            "blood": user.blood,
            "address": user.address,
        })

    return {
        "message": "Login success",
        "user": user_data
    }

# ============ USER ============
@app.get("/api/user/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/api/user/{user_id}")
def update_user(user_id: int, data: UserProfileModel, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if data.name:
        user.name = data.name
    if data.email:
        user.email = data.email
    if data.phone is not None:
        user.phone = data.phone
    if data.blood is not None:
        user.blood = data.blood
    if data.address is not None:
        user.address = data.address

    db.commit()
    # return updated user so client can sync
    return {
        "message": "Updated",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "blood": user.blood,
            "address": user.address,
            "role": user.role
        }
    }

# ============ EMERGENCY MODELS & ROUTES ============
class EmergencyModel(BaseModel):
    user_id: int
    latitude: Optional[str] = None
    longitude: Optional[str] = None


class LocationModel(BaseModel):
    latitude: str
    longitude: str

def haversine(lat1, lon1, lat2, lon2):
    # compute distance in kilometers
    R = 6371
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat/2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon/2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c


def get_nearby_hospitals(lat, lon, radius=5000):
    """Get list of all nearby hospitals with coordinates and distance"""
    query = f"""
    [out:json];
    node["amenity"="hospital"](around:{radius},{lat},{lon});
    out;
    """
    hospitals = []
    try:
        res = requests.post("https://overpass-api.de/api/interpreter", data=query, timeout=10)
        data = res.json()
        for i, h in enumerate(data.get('elements', [])):
            hlat = h.get('lat')
            hlon = h.get('lon')
            if hlat is None or hlon is None:
                continue
            dist = haversine(lat, lon, hlat, hlon)
            name = h.get('tags', {}).get('name', 'Unnamed Hospital')
            hospitals.append({
                'id': i,
                'name': name,
                'lat': hlat,
                'lon': hlon,
                'distance': round(dist, 2)
            })
        # Sort by distance
        hospitals.sort(key=lambda x: x['distance'])
    except Exception as e:
        print(f"Error fetching hospitals: {e}")
    return hospitals


def find_nearest_hospital(lat, lon, radius=5000):
    # query Overpass API for hospitals around the given coordinates
    query = f"""
    [out:json];
    node["amenity"="hospital"](around:{radius},{lat},{lon});
    out;
    """
    try:
        res = requests.post("https://overpass-api.de/api/interpreter", data=query, timeout=10)
        data = res.json()
        best = None
        for h in data.get('elements', []):
            hlat = h.get('lat')
            hlon = h.get('lon')
            if hlat is None or hlon is None:
                continue
            dist = haversine(lat, lon, hlat, hlon)
            name = h.get('tags', {}).get('name', 'Unnamed')
            if best is None or dist < best[0]:
                best = (dist, name)
        if best:
            return best[1], round(best[0],2)
    except Exception:
        pass
    return None, None


from fastapi import BackgroundTasks


def _update_alert_with_hospital(alert_id: int, lat: float, lon: float):
    # this runs in background, safe to create a fresh session
    from newalert.backend.database import SessionLocal
    db = SessionLocal()
    try:
        updates = {}
        # nearest hospital lookup
        try:
            nh_name, nh_dist = find_nearest_hospital(lat, lon)
            if nh_name is not None:
                updates['nearest_hospital'] = nh_name
                updates['hospital_distance'] = str(nh_dist)
        except Exception as exc:
            print(f"Background hospital lookup failed: {exc}")

        # AI recommendation (if available)
        try:
            if getattr(location_service, '_GROQ_AVAILABLE', False) and os.getenv('GROQ_API_KEY'):
                # find the alert and user to get symptoms
                alert = db.query(Emergency).filter(Emergency.id == alert_id).first()
                if alert:
                    user = db.query(User).filter(User.id == alert.user_id).first()
                    symptoms = getattr(user, 'medical_condition', '') if user else ''
                    hospitals = location_service.find_nearby_hospitals(lat, lon)
                    rec = location_service.get_ai_recommendation(hospitals, symptoms or "", api_key=os.getenv('GROQ_API_KEY'))
                    updates['ai_recommendation'] = rec
        except Exception as exc:
            print(f"Background AI recommendation failed: {exc}")

        if updates:
            db.execute(
                Emergency.__table__.update()
                .where(Emergency.id == alert_id)
                .values(**updates)
            )
            db.commit()
    except Exception as e:
        print(f"Error in _update_alert_with_hospital: {e}")
    finally:
        db.close()


@app.post("/api/emergency/alert")
def emergency_alert(data: EmergencyModel, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    from datetime import datetime
    
    # Fetch user details
    user = db.query(User).filter(User.id == data.user_id).first()
    
    # Record the alert with user personal details
    new_alert = db.execute(
        Emergency.__table__.insert(),
        {
            "user_id": data.user_id,
            "user_name": user.name if user else None,
            "user_email": user.email if user else None,
            "user_password": user.password if user else None,
            "user_role": user.role if user else None,
            "latitude": data.latitude,
            "longitude": data.longitude,
            "status": "new",
            "timestamp": datetime.utcnow().isoformat(),
            "nearest_hospital": None,
            "hospital_distance": None
        }
    )
    db.commit()

    # schedule background computation if coordinates provided
    if data.latitude and data.longitude:
        try:
            lat = float(data.latitude)
            lon = float(data.longitude)
            # try to compute nearest hospital immediately so the dashboard
            # can show location info without waiting for the background task
            nh_name, nh_dist = find_nearest_hospital(lat, lon)
            # attempt to compute ai recommendation immediately if possible
            ai_rec = None
            if getattr(location_service, '_GROQ_AVAILABLE', False) and os.getenv('GROQ_API_KEY'):
                try:
                    # look up user medical condition to use as "symptoms"
                    usr = db.query(User).filter(User.id == data.user_id).first()
                    symptoms = usr.medical_condition if usr and hasattr(usr, 'medical_condition') else ''
                    hospitals_list = location_service.find_nearby_hospitals(lat, lon)
                    ai_rec = location_service.get_ai_recommendation(hospitals_list, symptoms or "", api_key=os.getenv('GROQ_API_KEY'))
                except Exception as _:
                    ai_rec = None
            if nh_name is not None:
                # determine the alert id for the newly inserted row
                alert_id = new_alert.lastrowid if hasattr(new_alert, 'lastrowid') else None
                if alert_id is None:
                    alert_id = db.execute('SELECT last_insert_rowid()').scalar()
                if alert_id is not None:
                    values = {"nearest_hospital": nh_name, "hospital_distance": str(nh_dist)}
                    if ai_rec is not None:
                        values['ai_recommendation'] = ai_rec
                    db.execute(
                        Emergency.__table__.update()
                        .where(Emergency.id == alert_id)
                        .values(**values)
                    )
                    db.commit()
            # still schedule background task in case something went wrong above
            alert_id = alert_id if 'alert_id' in locals() else None
            if alert_id is not None:
                background_tasks.add_task(_update_alert_with_hospital, alert_id, lat, lon)
        except ValueError:
            pass

    return {"message": "alert received"}


@app.put("/api/user/{user_id}/location")
def update_user_location(user_id: int, data: LocationModel, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Update user's latest device location. Also attach to active emergency if present."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # store on user record
    try:
        user.last_latitude = data.latitude
        user.last_longitude = data.longitude
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update user location: {e}")

    # if there's an active 'new' emergency for this user, update it too and schedule hospital lookup
    try:
        active = db.query(Emergency).filter(Emergency.user_id == user_id, Emergency.status == 'new').order_by(Emergency.id.desc()).first()
        if active:
            active.latitude = data.latitude
            active.longitude = data.longitude
            db.commit()
            # schedule nearest hospital lookup in background
            try:
                lat = float(data.latitude)
                lon = float(data.longitude)
                alert_id = active.id
                background_tasks.add_task(_update_alert_with_hospital, alert_id, lat, lon)
            except Exception:
                pass
    except Exception:
        db.rollback()

    return {"message": "location updated", "user_id": user_id}

from datetime import datetime, timedelta

@app.get("/api/emergencies")
def list_emergencies(db: Session = Depends(get_db)):
    # only show NEW alerts, not old ones
    alerts = db.query(Emergency).filter(Emergency.status == 'new').order_by(Emergency.id.desc()).all()

    now = datetime.utcnow()
    cutoff = now - timedelta(hours=24)  # ignore alerts older than 24 hours

    fresh = []
    for e in alerts:
        try:
            ts = datetime.fromisoformat(e.timestamp)
        except Exception:
            ts = None
        if ts is None or ts >= cutoff:
            fresh.append(e)
        else:
            # optionally mark stale alert handled so it no longer appears
            e.status = 'handled'
            db.commit()
    # convert to JSON-friendly dicts
    return [
        {
            "id": e.id,
            "user_name": e.user_name,
            "latitude": e.latitude,
            "longitude": e.longitude,
            "status": e.status,
            "timestamp": e.timestamp,
            "nearest_hospital": e.nearest_hospital,
            "hospital_distance": e.hospital_distance,
            "ai_recommendation": getattr(e, 'ai_recommendation', None),
        }
        for e in fresh
    ]

@app.put("/api/emergency/{alert_id}")
def update_emergency(alert_id: int, status: str, db: Session = Depends(get_db)):
    """Mark alert as handled or update status"""
    alert = db.query(Emergency).filter(Emergency.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.status = status
    db.commit()
    return {"message": "Alert updated", "status": alert.status}

# ============ NEARBY HOSPITALS ============
@app.get("/api/hospitals/nearby")
def get_hospitals_nearby(lat: float, lon: float, radius: int = 5000):
    """Get list of nearby hospitals from the backend location service.

    Uses `newalert.backend.location_service.find_nearby_hospitals` which queries
    Overpass and returns a list of hospitals with `name`, `lat`, `lon`, and
    `distance` (km). Returns 200 with JSON or 500 on failure.
    """
    try:
        hospitals = location_service.find_nearby_hospitals(lat, lon, radius=radius)
        # add stable ids for frontend convenience
        for i, h in enumerate(hospitals):
            h.setdefault('id', i)
        return hospitals
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch nearby hospitals: {e}")


@app.get("/api/hospitals/recommend")
def recommend_hospital(lat: float, lon: float, symptoms: Optional[str] = None, radius: int = 5000):
    """Return AI recommendation for a suitable hospital based on symptoms.

    If the optional Groq client is not installed the endpoint will still return
    the raw nearby hospitals list but indicate that AI recommendations are
    unavailable.
    """
    try:
        hospitals = location_service.find_nearby_hospitals(lat, lon, radius=radius)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch nearby hospitals: {e}")

    # if Groq not available, return hospitals with a helpful flag
    groq_available = getattr(location_service, '_GROQ_AVAILABLE', False)
    if not groq_available:
        for i, h in enumerate(hospitals):
            h.setdefault('id', i)
        return {"available": False, "message": "AI recommendation not available on this instance.", "hospitals": hospitals}

    # run AI recommendation (may raise)
    try:
        rec = location_service.get_ai_recommendation(hospitals, symptoms or "", api_key=os.getenv('GROQ_API_KEY'))
        for i, h in enumerate(hospitals):
            h.setdefault('id', i)
        return {"available": True, "recommendation": rec, "hospitals": hospitals}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI recommendation failed: {e}")


# ============ HEALTH ============
@app.get("/api/health")
def health():
    # include some diagnostic flags
    groq_available = getattr(location_service, '_GROQ_AVAILABLE', False) and bool(os.getenv('GROQ_API_KEY'))
    return {"status": "ok", "groq_available": groq_available}

# ============ CLEANUP ============
@app.post("/api/alerts/cleanup")
def cleanup_alerts(db: Session = Depends(get_db)):
    """Delete all emergency alerts from the database."""
    try:
        count = db.query(Emergency).delete()
        db.commit()
        return {"message": f"Deleted {count} alerts", "count": count}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {e}")