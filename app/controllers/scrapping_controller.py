from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import httpx, os, asyncio
from app.database import get_db
from app.crud.lead import delete_leads_by_sector_city, create_lead
from app.models.lead import Lead
from app.schemas.lead import LeadOut
from app.models.city import City
from app.schemas.city import CityOut
from dotenv import load_dotenv
from app.auth import role_required

load_dotenv()
router = APIRouter(prefix="/leads", tags=["Leads"])

GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
TEXT_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"


# -------------------------------------------------------------------
# 1️⃣ SCRAPE AND SAVE LEADS
# -------------------------------------------------------------------
@router.post("/scrape", dependencies=[Depends(role_required(["Admin"]))])
async def scrape_leads(
    sector: str = Query(..., description="Business sector, e.g. cafe, salon, gym"),
    city: str = Query(..., description="City name, e.g. Kolkata, Pune"),
    db: Session = Depends(get_db)
):

    if not GOOGLE_PLACES_API_KEY:
        raise HTTPException(status_code=500, detail="Google Places API key not configured")

    next_page_token = None
    created_count = 0
    skipped_count = 0

    async with httpx.AsyncClient(timeout=20.0) as client:
        while True:
            params = {
                "query": f"{sector} in {city}",
                "key": GOOGLE_PLACES_API_KEY
            }
            if next_page_token:
                params["pagetoken"] = next_page_token
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

                # Fetch details (phone, website)
                details_params = {
                    "place_id": place_id,
                    "fields": "formatted_phone_number,website",
                    "key": GOOGLE_PLACES_API_KEY
                }
                details_res = await client.get(DETAILS_URL, params=details_params)
                details = details_res.json().get("result", {})

                phone = details.get("formatted_phone_number")

                # ✅ Skip if phone is missing or already exists
                if not phone:
                    skipped_count += 1
                    continue

                existing_lead = db.query(Lead).filter(
                    Lead.phone == phone,
                    Lead.city == city,
                    Lead.sector == sector
                ).first()

                if existing_lead:
                    skipped_count += 1
                    continue

                lead_data = {
                    "sector": sector,
                    "city": city,
                    "phone": phone,
                    "email": None,
                    "address": address,
                    "summary": f"{name} | Rating: {rating or 'N/A'} ({user_ratings or 0} reviews)"
                }

                create_lead(db, lead_data)
                created_count += 1

            next_page_token = data.get("next_page_token")
            if not next_page_token:
                break

    return {
        "message": f"Scraping completed successfully. {created_count} new leads added, {skipped_count} skipped (existing or invalid)."
    }


# -------------------------------------------------------------------
# 2️⃣ FETCH LEADS (with pagination & filtering)
# -------------------------------------------------------------------
@router.get("/", response_model=dict, dependencies=[Depends(role_required(["Admin"]))])
def get_leads(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    sector: str | None = Query(None, description="Filter by business sector"),
    city: str | None = Query(None, description="Filter by city")
):
    query = db.query(Lead)

    # Apply filters dynamically
    if sector:
        query = query.filter(Lead.sector == sector)
    if city:
        query = query.filter(Lead.city == city)

    total = query.count()
    leads = (
        query.order_by(Lead.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    leads_out: List[LeadOut] = [LeadOut.from_orm(l) for l in leads]

    return {
        "data": {
            "leads": leads_out,
            "meta": {
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total + limit - 1) // limit,
                "sector": sector,
                "city": city,
            },
        }
    }
    
@router.get("/cities", response_model=dict, dependencies=[Depends(role_required(["Admin"]))])
def list_cities(
    db: Session = Depends(get_db),
    keyword: str | None = Query(None, description="Search by city name")
):
    query = db.query(City)
    if keyword:
        query = query.filter(City.title.ilike(f"{keyword}%"))

    cities = query.order_by(City.title.asc()).all()
    cities_out: List[CityOut] = [CityOut.from_orm(c) for c in cities]

    return {"data": {"cities": cities_out, "count": len(cities_out)}}