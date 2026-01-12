from app.models.skill import Skill
from app.models.tool import Tool
from app.models.package_type import PackageType
from typing import List, Type, TypeVar
from sqlalchemy.orm import Session

T = TypeVar("T")


def fetch_by_ids(
    db: Session,
    model: Type[T],
    ids: List[int] | None,
) -> List[T]:
    """
    Generic helper to fetch records by ID list.
    Returns empty list if ids is None or empty.
    """
    if not ids:
        return []

    return db.query(model).filter(model.id.in_(ids)).all()


def fetch_skills(db: Session, skill_ids: list[int] | None):
    return fetch_by_ids(db, Skill, skill_ids)


def fetch_tools(db: Session, tool_ids: list[int] | None):
    return fetch_by_ids(db, Tool, tool_ids)


def fetch_dependencies(db: Session, dependency_ids: list[int] | None):
    return fetch_by_ids(db, PackageType, dependency_ids)
