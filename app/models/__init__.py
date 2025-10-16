# app/models/__init__.py
# from .apps import Apps
from app.models.users import User

from sqlalchemy.orm import declarative_base
Base = declarative_base()
