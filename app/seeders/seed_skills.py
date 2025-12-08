from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.skill import Skill

SKILLS = [
    "n8n",
    "Python",
    "OpenAI",
    "PostgreSQL",
    "Zapier",
    "AWS",
]


def seed_skills():
    db = SessionLocal()

    for name in SKILLS:
        # Check exists
        existing = db.query(Skill).filter_by(name=name).first()
        if not existing:
            db.add(Skill(name=name))

    db.commit()
    db.close()


if __name__ == "__main__":
    seed_skills()
    print("Skills seeded successfully!")
