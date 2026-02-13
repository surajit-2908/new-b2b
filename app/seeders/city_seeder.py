import csv
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.city import City
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, "2025_Gaz_place_national.txt")

def seed_us_cities():
    db: Session = SessionLocal()
    inserted = 0

    try:
        with open(FILE_PATH, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter='|')

            for row in reader:
                city = City(
                    title=row["NAME"],
                    state=row["USPS"],
                    geoid=row["GEOID"],
                    latitude=float(row["INTPTLAT"]),
                    longitude=float(row["INTPTLONG"])
                )

                db.add(city)
                inserted += 1

        db.commit()
        print(f"✅ Inserted {inserted} US cities successfully.")

    except Exception as e:
        db.rollback()
        print("❌ Error:", e)

    finally:
        db.close()


if __name__ == "__main__":
    seed_us_cities()
