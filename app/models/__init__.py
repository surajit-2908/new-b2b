# app/models/__init__.py

# Import the global Base from database.py
from app.database import Base

# Import all models so Alembic can detect them
from app.models.user import User
from app.models.lead import Lead
from app.models.user_city_sector import UserCitySector
from app.models.deal import Deal
from app.models.work_package import WorkPackage
from app.models.technical_context import TechnicalContext
from app.models.communication import Communication
from app.models.lead_free_note import LeadFreeNote
from app.models.internal_note import InternalNote
from app.models.sector_package import SectorPackage
from app.models.package_type import PackageType


# NOTE:
# Do NOT redefine Base here.
# Just importing models ensures metadata is populated.
