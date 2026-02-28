from database import SessionLocal, User
from .auth import hash_password

db = SessionLocal()

user1 = User(
    name="Rohith",
    email="rohith@gmail.com",
    password=hash_password("123456"),
    role="user",
    is_verified=1
)

user2 = User(
    name="City Hospital",
    email="hospital@gmail.com",
    password=hash_password("123456"),
    role="receiver",
    is_verified=1
)

db.add(user1)
db.add(user2)
db.commit()
db.close()

print("Sample data inserted successfully!")