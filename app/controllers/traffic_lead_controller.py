from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone
import requests, os
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Lead
from app.database import get_db
from app.schemas.traffic_lead import TrafficLeadCreate

load_dotenv()

router = APIRouter(prefix="/traffic-lead", tags=["Traffic Leads"])

TYPEFORM_API_KEY = os.getenv("TYPEFORM_API_KEY")
FORM_ID = os.getenv("FORM_ID")

TYPEFORM_RESPONSES_URL = f"https://api.typeform.com/forms/{FORM_ID}/responses"
TYPEFORM_FORM_URL = f"https://api.typeform.com/forms/{FORM_ID}"

HEADERS = {
    "Authorization": f"Bearer {TYPEFORM_API_KEY}"
}

REQUIRED_FIELDS = ["city", "sector", "phone", "email", "address"]


# ⚠️ FOR TESTING ONLY
@router.get("/typeform-responses")
def get_typeform_responses():
    db: Session = SessionLocal()

    try:
        # 1️⃣ Fetch form schema
        form_res = requests.get(
            TYPEFORM_FORM_URL,
            headers=HEADERS,
            timeout=10
        )
        if form_res.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch form schema")

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
            raise HTTPException(
                status_code=response.status_code,
                detail="Failed to fetch Typeform data"
            )

        data = response.json()

        table = []
        saved_count = 0
        skipped_count = 0

        for item in data.get("items", []):
            response_id = item.get("response_id")
            submitted_at = item.get("submitted_at")

            if not response_id:
                skipped_count += 1
                continue

            # Deduplication
            exists = (
                db.query(Lead.id)
                .filter(Lead.response_id == response_id)
                .first()
            )

            # Build answer map
            answers = {}
            for answer in item.get("answers", []):
                field_id = answer["field"]["id"]
                field_type = answer["type"]
                answers[field_map.get(field_id, field_id)] = answer.get(field_type)

            row = {
                "Response ID": response_id,
                "Submitted At": submitted_at,
                **answers
            }
            table.append(row)

            if exists:
                skipped_count += 1
                continue

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
                lead_status="Qualified Lead",
                created_at=datetime.now(timezone.utc)
            )

            db.add(lead)
            saved_count += 1

        db.commit()

        return {
            "total": len(table),
            "saved": saved_count,
            "skipped": skipped_count,
            "rows": table
        }

    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Typeform API timeout")

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()


@router.post("/create", response_model=dict)
def create_traffic_lead(lead_data: TrafficLeadCreate, db: Session = Depends(get_db)):

    # Create traffic lead
    lead = Lead(
        city=lead_data.city,
        sector=lead_data.sector,
        phone=lead_data.phone,
        email=lead_data.email,
        address=lead_data.address,
        summary=lead_data.summary,
        lead_type="Traffic Lead",
        lead_status="Qualified Lead",
        created_at=datetime.now(timezone.utc)
    )

    db.add(lead)
    db.commit()
    db.refresh(lead)

    return {"message": "Data saved successfully"}