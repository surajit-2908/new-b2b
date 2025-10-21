from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import httpx, os, asyncio
from app.database import get_db
from app.crud.lead import delete_leads_by_sector_city, create_lead
from app.schemas.lead import LeadOut
from dotenv import load_dotenv

load_dotenv()
router = APIRouter(prefix="/leads", tags=["Leads"])

GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
TEXT_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"


@router.post("/scrape", response_model=List[LeadOut])
async def scrape_leads(
    sector: str = Query(...),
    city: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Scrape leads using Google Places API (Text Search + Details)
    """
    if not GOOGLE_PLACES_API_KEY:
        raise HTTPException(status_code=500, detail="Google Places API key not configured")

    # Clear previous leads for this sector + city
    delete_leads_by_sector_city(db, sector, city)

    all_leads = []
    next_page_token = None

    async with httpx.AsyncClient(timeout=20.0) as client:
        while True:
            params = {
                "query": f"{sector} in {city}",
                "key": GOOGLE_PLACES_API_KEY
            }
            if next_page_token:
                params["pagetoken"] = next_page_token
                # Google API delay for next_page_token to activate
                await asyncio.sleep(2)

            resp = await client.get(TEXT_SEARCH_URL, params=params)
            data = resp.json()

            if "error_message" in data:
                raise HTTPException(status_code=400, detail=data["error_message"])

            for place in data.get("results", []):
                place_id = place.get("place_id")
                name = place.get("name")
                address = place.get("formatted_address")
                rating = place.get("rating")
                user_ratings = place.get("user_ratings_total")

                # Fetch details (like phone, website)
                details_params = {
                    "place_id": place_id,
                    "fields": "formatted_phone_number,website",
                    "key": GOOGLE_PLACES_API_KEY
                }
                details_res = await client.get(DETAILS_URL, params=details_params)
                details = details_res.json().get("result", {})

                lead_data = {
                    "sector": sector,
                    "city": city,
                    "phone": details.get("formatted_phone_number"),
                    "email": None,  # Google Places doesn’t provide email
                    "address": address,
                    "summary": f"{name} | Rating: {rating or 'N/A'} ({user_ratings or 0} reviews)"
                }

                lead = create_lead(db, lead_data)
                all_leads.append(lead)

            next_page_token = data.get("next_page_token")
            if not next_page_token:
                break

    return all_leads
