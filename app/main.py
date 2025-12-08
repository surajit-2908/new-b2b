from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.controllers import (
    auth_controller,
    communication_controller,
    deal_controller,
    internal_note_controller,
    lead_note_controller,
    technical_context_controller,
    user_controller,
    scrapping_controller,
    user_city_sector_controller,
    technician_controller,
    work_package_controller,
)
from app.database import engine, Base

app = FastAPI()

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(auth_controller.router)
app.include_router(user_controller.router)
app.include_router(scrapping_controller.router)
app.include_router(user_city_sector_controller.router)
app.include_router(technician_controller.router)
app.include_router(lead_note_controller.router)
app.include_router(deal_controller.router)
app.include_router(technical_context_controller.router)
app.include_router(communication_controller.router)
app.include_router(internal_note_controller.router)
app.include_router(work_package_controller.router)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.on_event("startup")
def on_startup():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
