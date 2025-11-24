# app/models/__init__.py

# Import the global Base from database.py
from app.database import Base

# Import all models so Alembic can detect them
from app.models.user import User
from app.models.lead import Lead
from app.models.user_city_sector import UserCitySector

# NOTE:
# Do NOT redefine Base here.
# Just importing models ensures metadata is populated.
