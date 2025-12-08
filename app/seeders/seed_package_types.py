from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.package_type import PackageType

PACKAGE_TYPES = [
    "LLM / NLP",
    "Workflow Automation (n8n / Zapier / Make)",
    "API Integration",
    "CRM Integration",
    "ERP Integration",
    "Database / Data Pipeline",
    "Internal Dashboard / Reporting",
    "Custom Script or Microservice",
    "Frontend UI Work",
    "Backend System Integration",
    "QA / Testing Automation",
    "Other (Specify)",
]


def seed_package_types():
    db = SessionLocal()

    for name in PACKAGE_TYPES:
        # Check exists
        existing = db.query(PackageType).filter_by(name=name).first()
        if not existing:
            db.add(PackageType(name=name))

    db.commit()
    db.close()


if __name__ == "__main__":
    seed_package_types()
    print("Package types seeded successfully!")
