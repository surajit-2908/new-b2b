from fastapi import APIRouter, HTTPException
import requests, os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/traffic-lead", tags=["Traffic Leads"])

TYPEFORM_API_KEY = os.getenv("TYPEFORM_API_KEY")
FORM_ID = os.getenv("FORM_ID") 
TYPEFORM_RESPONSES_URL = f"https://api.typeform.com/forms/{FORM_ID}/responses"
TYPEFORM_FORM_URL = f"https://api.typeform.com/forms/{FORM_ID}"

HEADERS = {
    "Authorization": f"Bearer {TYPEFORM_API_KEY}"
}

# for testing purpose only 
@router.get("/typeform-responses")
def get_typeform_responses():
    # 1️⃣ Fetch form schema (questions)
    form_res = requests.get(TYPEFORM_FORM_URL, headers=HEADERS)
    if form_res.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to fetch form schema")

    form_data = form_res.json()

    # Build field_id → question title map
    field_map = {}
    for field in form_data.get("fields", []):
        field_map[field["id"]] = field["title"]

    # Fetch responses
    response = requests.get(TYPEFORM_RESPONSES_URL, headers=HEADERS)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch Typeform data")

    data = response.json()

    table = []

    for item in data.get("items", []):
        row = {
            "Response ID": item.get("response_id"),
            "Submitted At": item.get("submitted_at"),
        }

        for answer in item.get("answers", []):
            field_id = answer["field"]["id"]
            field_type = answer["type"]
            value = answer.get(field_type)

            field_name = field_map.get(field_id, field_id)  # fallback to ID
            row[field_name] = value

        table.append(row)

    return {
        "total": len(table),
        "rows": table
    }