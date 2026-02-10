from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from apscheduler.schedulers.background import BackgroundScheduler
from app.database import engine, Base
from app.scheduler.bidding_scheduler import auto_assign_lowest_bidder
from app.scheduler.traffic_leads import sync_typeform_leads
from app.controllers import (
    auth_controller,
    communication_controller,
    deal_controller,
    internal_note_controller,
    lead_note_controller,
    organic_lead_controller,
    traffic_lead_controller,
    technical_context_controller,
    user_controller,
    scrapping_controller,
    user_city_sector_controller,
    technician_controller,
    work_package_controller,
)
 
app = FastAPI()

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- Routes ----------------
app.include_router(auth_controller.router)
app.include_router(user_controller.router)
app.include_router(scrapping_controller.router)
app.include_router(user_city_sector_controller.router)  # prefix : /assign-user
app.include_router(technician_controller.router)
app.include_router(lead_note_controller.router)
app.include_router(deal_controller.router)
app.include_router(technical_context_controller.router)
app.include_router(communication_controller.router)
app.include_router(internal_note_controller.router)
app.include_router(work_package_controller.router)
app.include_router(organic_lead_controller.router)
app.include_router(traffic_lead_controller.router)

# ---------------- Static ----------------
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ---------------- Scheduler ----------------
scheduler = BackgroundScheduler(timezone="UTC")

@app.on_event("startup")
def on_startup():
    print("Starting application...")
    # Base.metadata.create_all(bind=engine)

    # 1️⃣ Hourly bidding assignment
    scheduler.add_job(
        auto_assign_lowest_bidder,
        trigger="interval",
        minutes=1,                   # ⏱️ RUNS HOURLY
        id="auto_assign_bidding",
        replace_existing=True,
        max_instances=1,           # safety
        coalesce=True              # skip missed runs
    )
    
    # 2️⃣ Daily Typeform sync
    scheduler.add_job(
        sync_typeform_leads,
        trigger="cron",
        hour=2,                    # 🕑 runs daily at 02:00 UTC
        minute=0,
        id="sync_typeform_leads",
        replace_existing=True,
        max_instances=1,
        coalesce=True
    )

    scheduler.start()
    print("Bidding auto-assignment scheduler started (hourly).")

@app.on_event("shutdown")
def on_shutdown():
    scheduler.shutdown()
    print("Scheduler stopped.")
 