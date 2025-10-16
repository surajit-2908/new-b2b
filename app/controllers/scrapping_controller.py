from fastapi import APIRouter, Query, HTTPException, Depends
import httpx
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud.lead import get_leads_by_sector_city, delete_leads_by_sector_city, create_lead
from app.schemas.lead import LeadOut
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

router = APIRouter(prefix="/leads", tags=["Leads"])

GOOGLE_PLACES_TEXT_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
GOOGLE_PLACE_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"

@router.post("/scrape", response_model=List[LeadOut])
async def scrape_leads(
    sector: str = Query(...),
    city: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Scrape leads from Google Places API and save them to DB.
    Deletes old leads for the same sector+city combination.
    """

    if not sector or not city:
        raise HTTPException(status_code=400, detail="Sector and city are required.")

    # Remove old leads for this combination
    delete_leads_by_sector_city(db, sector, city)

    all_leads = []
    next_page_token = None

    async with httpx.AsyncClient(timeout=20.0) as client:
        while True:
            params = {
                "query": f"{sector} {city}",
                "key": GOOGLE_PLACES_API_KEY
            }
            if next_page_token:
                params["pagetoken"] = next_page_token

            r = await client.get(GOOGLE_PLACES_TEXT_SEARCH_URL, params=params)
            data = r.json()

            for place in data.get("results", []):
                place_id = place.get("place_id")
                name = place.get("name")
                address = place.get("formatted_address")
                summary = f"Rating: {place.get('rating')}, Total Ratings: {place.get('user_ratings_total')}"

                # Optional: Get phone/email from Place Details
                details_params = {
                    "place_id": place_id,
                    "fields": "formatted_phone_number,website",
                    "key": GOOGLE_PLACES_API_KEY
                }
                details_res = await client.get(GOOGLE_PLACE_DETAILS_URL, params=details_params)
                details = details_res.json().get("result", {})

                lead_data = {
                    "sector": sector,
                    "city": city,
                    "phone": details.get("formatted_phone_number"),
                    "email": None,  # Google Places does not provide email
                    "address": address,
                    "summary": summary
                }

                lead = create_lead(db, lead_data)
                all_leads.append(lead)

            # Pagination
            next_page_token = data.get("next_page_token")
            if not next_page_token:
                break

    return all_leads
