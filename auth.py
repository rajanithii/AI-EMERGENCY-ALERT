import random
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from newalert.backend.database import User

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def generate_otp():
    return str(random.randint(100000, 999999))

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()