from app.database import get_db
from app.models.package_type import PackageType
from app.models.skill import Skill
from app.models.tool import Tool
from app.schemas.work_package import PackageTypeOut, SkillsOut, ToolsOut
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/work-package", tags=["Work Package"])


@router.get("/get-package-types", response_model=list[PackageTypeOut])
def get_package_types(db: Session = Depends(get_db)):
    packages = db.query(PackageType).all()

    return packages


@router.get("/get-skills", response_model=list[SkillsOut])
def get_skills(db: Session = Depends(get_db)):
    skills = db.query(Skill).all()

    return skills


@router.get("/get-tools", response_model=list[ToolsOut])
def get_tools(db: Session = Depends(get_db)):
    tools = db.query(Tool).all()

    return tools
