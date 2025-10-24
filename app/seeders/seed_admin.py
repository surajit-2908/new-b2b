from app.database import SessionLocal
from app.models.user import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

db = SessionLocal()

existing = db.query(User).filter(User.email == "admin@example.com").first()
if not existing:
    admin = User(
        name="Admin",
        email="admin@admin.com",
        role="Admin",
        password=pwd_context.hash("admin123")
    )
    db.add(admin)
    db.commit()
    print("Admin user created successfully!")
else:
    print("Admin user already exists")
