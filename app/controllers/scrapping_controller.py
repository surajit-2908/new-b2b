import asyncio
import httpx
from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import httpx, os, asyncio
from app.database import get_db
from app.crud.lead import create_lead
from app.models.lead import Lead
from app.schemas.lead import LeadOut
from app.models.city import City
from app.schemas.city import CityOut
from app.models.sector import Sector
from app.schemas.sector import SectorOut
from dotenv import load_dotenv
from app.auth import role_required
from app.utils.pagination import paginate

load_dotenv()
router = APIRouter(prefix="/leads", tags=["Leads"])

GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"
NEARBY_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"

# Radius (in meters) per grid search
SEARCH_RADIUS = 5000  # 5 km per grid
GRID_STEP = 0.1       # degrees ~11 km (tweak for more/fewer queries)

async def get_city_coordinates(city: str) -> tuple[float, float]:
    """Fetch city center coordinates using Google Geocoding API."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        params = {"address": city, "key": GOOGLE_PLACES_API_KEY}
        res = await client.get(GEOCODE_URL, params=params)
        data = res.json()
        if not data.get("results"):
            raise HTTPException(status_code=404, detail=f"City not found: {city}")
        loc = data["results"][0]["geometry"]["location"]
        return loc["lat"], loc["lng"]

# -------------------------------------------------------------------
# 1️⃣ SCRAPE AND SAVE LEADS
# -------------------------------------------------------------------
@router.post("/scrape", dependencies=[Depends(role_required(["Admin"]))])
async def scrape_city_leads(
    sector: str = Query(..., description="Business sector, e.g. cafe, salon, gym"),
    city: str = Query(..., description="City name, e.g. Kolkata, Pune"),
    db: Session = Depends(get_db)
):
    """Scrape leads citywide by generating a coordinate grid around the city."""
    city_lat, city_lng = await get_city_coordinates(city)
    created_count, skipped_count = 0, 0

    async with httpx.AsyncClient(timeout=20.0) as client:
        tasks = []

        # Build grid (±GRID_STEP degrees around city center)
        for i in range(-3, 4):  # 7x7 grid => 49 search points
            for j in range(-3, 4):
                lat = city_lat + (i * GRID_STEP)
                lng = city_lng + (j * GRID_STEP)
                tasks.append(fetch_grid_data(client, db, lat, lng, sector, city))

        results = await asyncio.gather(*tasks)
        for created, skipped in results:
            created_count += created
            skipped_count += skipped

    return {
        "message": f"Scraping completed successfully for {city}. "
                   f"{created_count} new leads added, {skipped_count} skipped (duplicates)."
    }


async def fetch_grid_data(client, db, lat, lng, sector, city):
    """Fetch nearby results from one grid point (with pagination)."""
    created, skipped = 0, 0
    next_page_token = None

    while True:
        params = {
            "location": f"{lat},{lng}",
            "radius": SEARCH_RADIUS,
            "keyword": sector,
            "key": GOOGLE_PLACES_API_KEY
        }
        if next_page_token:
            params["pagetoken"] = next_page_token
            await asyncio.sleep(2.5)  # required delay before using next_page_token

        res = await client.get(NEARBY_URL, params=params)
        data = res.json()

        if "error_message" in data:
            print(f"Error: {data['error_message']}")
            break

        for place in data.get("results", []):
            place_id = place.get("place_id")
            name = place.get("name")
            address = place.get("vicinity")
            rating = place.get("rating")
            user_ratings = place.get("user_ratings_total")

            if not place_id:
                skipped += 1
                continue

            # Check duplicates by place_id
            existing = db.query(Lead).filter(Lead.place_id == place_id).first()
            if existing:
                skipped += 1
                continue

            # Get details (phone, website)
            details_params = {
                "place_id": place_id,
                "fields": "formatted_phone_number,website",
                "key": GOOGLE_PLACES_API_KEY
            }
            details_res = await client.get(DETAILS_URL, params=details_params)
            details = details_res.json().get("result", {})

            lead_data = {
                "place_id": place_id,
                "sector": sector,
                "city": city,
                "phone": details.get("formatted_phone_number"),
                "email": None,
                "address": address,
                "summary": f"{name} | Rating: {rating or 'N/A'} ({user_ratings or 0} reviews)"
            }

            create_lead(db, lead_data)
            created += 1

        next_page_token = data.get("next_page_token")
        if not next_page_token:
            break

    return created, skipped

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

    leads, meta = paginate(query.order_by(Lead.created_at.desc()), page, limit)

    leads_out: List[LeadOut] = [LeadOut.from_orm(l) for l in leads]

    return {
        "data": {
            "leads": leads_out,
            "meta": {
                "total": meta["total"],
                "page": meta["page"],
                "limit": meta["limit"],
                "pages": meta["pages"],
                "sector": sector,
                "city": city,
            },
        }
    }
    
@router.get("/cities", response_model=dict, dependencies=[Depends(role_required(["Admin", "Technician", "User"]))])
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

@router.get("/sectors", response_model=dict, dependencies=[Depends(role_required(["Admin", "Technician", "User"]))])
def list_sectors(
    db: Session = Depends(get_db),
    keyword: str | None = Query(None, description="Search by sector name"),
    limit: int = Query(20, ge=1, le=100, description="Number of sectors to return"),
    page: int = Query(1, ge=1, description="Page number for pagination")
):
    query = db.query(Sector)
    if keyword:
        query = query.filter(Sector.name.ilike(f"%{keyword}%"))

    sectors, meta = paginate(query.order_by(Sector.created_at.desc()), page, limit)

    sectors_out: List[SectorOut] = [SectorOut.from_orm(c) for c in sectors]

    return {
        "data": {
            "sectors": sectors_out,
            "meta": meta
        }
    }
