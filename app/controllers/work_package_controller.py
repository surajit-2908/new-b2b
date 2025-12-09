from app.auth import role_required
from app.database import get_db
from app.models.deal import Deal
from app.models.package_type import PackageType
from app.models.skill import Skill
from app.models.tool import Tool
from app.models.work_package import WorkPackage
from app.schemas.work_package import (
    PackageTypeOut,
    SkillsOut,
    ToolsOut,
    WorkPackageCreate,
)
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException

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


@router.post(
    "/save",
    response_model=dict,
    dependencies=[Depends(role_required(["Admin", "User"]))],
)
def create_or_update_work_packages(
    data: WorkPackageCreate, db: Session = Depends(get_db)
):
    """
    Create or update work for a deal.
    """
    
    # Validate deal
    deal = db.query(Deal).filter(Deal.id == data.deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found.")

    saved_packages = []

    for pkg in data.packages:
        # Validate package type
        exists = (
            db.query(PackageType).filter(PackageType.id == pkg.package_type_id).first()
        )

        if not exists:
            raise HTTPException(status_code=400, detail="Invalid package type id")

        # Validate skills/tools/dependencies
        validate_tool_ids(pkg.primary_tools_ids, db)
        validate_skill_ids(pkg.required_skills_ids, db)
        validate_dependencies_ids(pkg.dependencies_ids, db)

        # UPDATE
        if pkg.package_id:
            wp = db.query(WorkPackage).filter(WorkPackage.id == pkg.package_id).first()

            if not wp:
                raise HTTPException(status_code=404, detail="Package not found")

            wp.package_title = pkg.package_title
            wp.package_type_id = pkg.package_type_id
            wp.package_summary = pkg.package_summary
            wp.custom_package_type = pkg.custom_package_type
            wp.key_deliverables = pkg.key_deliverables
            wp.acceptance_criteria = pkg.acceptance_criteria
            wp.required_skills_ids = pkg.required_skills_ids
            wp.primary_tools_ids = pkg.primary_tools_ids
            wp.package_estimated_complexity = pkg.package_estimated_complexity
            wp.package_price_allocation = pkg.package_price_allocation
            wp.dependencies_ids = pkg.dependencies_ids
            wp.status = "draft"

            saved_packages.append(wp)

        # CREATE
        else:
            new_wp = WorkPackage(
                deal_id=data.deal_id,
                package_title=pkg.package_title,
                package_type_id=pkg.package_type_id,
                package_summary=pkg.package_summary,
                custom_package_type=pkg.custom_package_type,
                key_deliverables=pkg.key_deliverables,
                acceptance_criteria=pkg.acceptance_criteria,
                required_skills_ids=pkg.required_skills_ids,
                primary_tools_ids=pkg.primary_tools_ids,
                package_estimated_complexity=pkg.package_estimated_complexity,
                package_price_allocation=pkg.package_price_allocation,
                dependencies_ids=pkg.dependencies_ids,
                status="draft",
                draft_version=1,
            )

            db.add(new_wp)
            saved_packages.append(new_wp)

    db.commit()

    return {"message": "Work packages saved/updated successfully"}


def validate_tool_ids(tool_ids: list[int], db: Session):
    if not tool_ids:
        raise HTTPException(status_code=400, detail="Tools is required")

    # Get existing tool IDs from DB
    existing_ids = db.query(Tool.id).filter(Tool.id.in_(tool_ids)).all()

    existing_ids = [t[0] for t in existing_ids]

    # Find missing IDs
    missing = set(tool_ids) - set(existing_ids)

    if missing:
        raise HTTPException(status_code=400, detail="Invalid tool ids")

    return True


def validate_skill_ids(skill_ids: list[int], db: Session):
    if not skill_ids:
        raise HTTPException(status_code=400, detail="Skill is required")

    # Get existing skill IDs from DB
    existing_ids = db.query(Skill.id).filter(Skill.id.in_(skill_ids)).all()

    existing_ids = [t[0] for t in existing_ids]

    # Find missing IDs
    missing = set(skill_ids) - set(existing_ids)

    if missing:
        raise HTTPException(status_code=400, detail="Invalid skill ids")

    return True


def validate_dependencies_ids(dependencies_ids: list[int], db: Session):
    if not dependencies_ids:
        raise HTTPException(status_code=400, detail="dependencies id is required")

    # Get existing skill IDs from DB
    existing_ids = db.query(PackageType.id).filter(PackageType.id.in_(dependencies_ids)).all()

    existing_ids = [t[0] for t in existing_ids]

    # Find missing IDs
    missing = set(dependencies_ids) - set(existing_ids)

    if missing:
        raise HTTPException(status_code=400, detail="Invalid dependencies ids")

    return True
