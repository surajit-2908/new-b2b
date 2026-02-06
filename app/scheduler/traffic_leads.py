from datetime import datetime, timezone
import os, requests
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from app.database import SessionLocal
from app.models import Lead

load_dotenv()

TYPEFORM_API_KEY = os.getenv("TYPEFORM_API_KEY")
FORM_ID = os.getenv("FORM_ID")

TYPEFORM_RESPONSES_URL = f"https://api.typeform.com/forms/{FORM_ID}/responses"
TYPEFORM_FORM_URL = f"https://api.typeform.com/forms/{FORM_ID}"

HEADERS = {
    "Authorization": f"Bearer {TYPEFORM_API_KEY}"
}

REQUIRED_FIELDS = ["city", "sector", "phone", "email", "address"]


def sync_typeform_leads():
    db: Session = SessionLocal()

    try:
        # 1️⃣ Fetch form schema
        form_res = requests.get(
            TYPEFORM_FORM_URL,
            headers=HEADERS,
            timeout=10
        )
        if form_res.status_code != 200:
            raise Exception("Failed to fetch Typeform schema")

        field_map = {
            field["id"]: field["title"]
            for field in form_res.json().get("fields", [])
        }

        # 2️⃣ Fetch responses
        response = requests.get(
            TYPEFORM_RESPONSES_URL,
            headers=HEADERS,
            timeout=10
        )
        if response.status_code != 200:
            raise Exception("Failed to fetch Typeform responses")

        data = response.json()
        saved_count = 0
        skipped_count = 0

        for item in data.get("items", []):
            response_id = item.get("response_id")
            if not response_id:
                skipped_count += 1
                continue

            # 🔒 Deduplication
            exists = (
                db.query(Lead.id)
                .filter(Lead.response_id == response_id)
                .first()
            )
            if exists:
                skipped_count += 1
                continue

            # Build answer map
            answers = {}
            for answer in item.get("answers", []):
                field_id = answer["field"]["id"]
                field_type = answer["type"]
                answers[field_map.get(field_id, field_id)] = answer.get(field_type)

            # ✅ Required field validation
            if any(not answers.get(field) for field in REQUIRED_FIELDS):
                skipped_count += 1
                continue

            # 💾 Save lead
            lead = Lead(
                response_id=response_id,
                city=answers.get("city"),
                sector=answers.get("sector"),
                phone=answers.get("phone"),
                email=answers.get("email"),
                address=answers.get("address"),
                summary=answers.get("summary"),
                lead_type="Traffic Lead",
                created_at=datetime.now(timezone.utc)
            )

            db.add(lead)
            saved_count += 1

        db.commit()

        print(
            f"Typeform sync completed | "
            f"Saved: {saved_count}, Skipped: {skipped_count}"
        )

    except Exception as e:
        db.rollback()
        print("Typeform sync error:", e)

    finally:
        print("Typeform scheduler executed at:", datetime.now(timezone.utc))
        db.close()
