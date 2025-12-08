from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.tool import Tool

PACKAGE_TYPES = [
    "n8n",
    "OpenAI API",
    "Slack",
    "HubSpot",
]


def seed_tools():
    db = SessionLocal()

    for name in PACKAGE_TYPES:
        # Check exists
        existing = db.query(Tool).filter_by(name=name).first()
        if not existing:
            db.add(Tool(name=name))

    db.commit()
    db.close()


if __name__ == "__main__":
    seed_tools()
    print("Tools seeded successfully!")
