from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.sector_package import SectorPackage

SECTOR_PACKAGES = [
    "Hospitality Package",
    "Healthcare Package",
    "Real Estate Package",
    "eCommerce Package",
    "Professional Services Package",
    "Finance & Accounting Package",
    "Manufacturing Package",
    "Logistics & Supply Chain Package",
    "Generic Automation Package",
    "Marketing Package",
    "Custom Solution",
    "Other (Specify)"
]


def seed_sector_packages():
    db = SessionLocal()

    for name in SECTOR_PACKAGES:
        # Check exists
        existing = db.query(SectorPackage).filter_by(name=name).first()
        if not existing:
            db.add(SectorPackage(name=name))

    db.commit()
    db.close()


if __name__ == "__main__":
    seed_sector_packages()
    print("Sector packages seeded successfully!")
