from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.seeders.seed_admin import seed_admin
from app.seeders.seed_sector_packages import seed_sector_packages
from app.seeders.seed_package_types import seed_package_types
from app.seeders.seed_skills import seed_skills
from app.seeders.seed_tools import seed_tools

if __name__ == "__main__":
    # seed_admin()
    # seed_sector_packages()
    seed_package_types()
    seed_skills()
    seed_tools()
    print("Database seeded successfully!")
