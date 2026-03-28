from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import db_session_dependency
from app.db.repositories.scholarship_repository import ScholarshipRepository
from app.domain.schemas.scholarship import ScholarshipOut
from app.domain.services.scholarship_service import ScholarshipService

router = APIRouter(prefix="/scholarships", tags=["scholarships"])


@router.get("", response_model=list[ScholarshipOut])
async def list_scholarships(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(db_session_dependency),
) -> list[ScholarshipOut]:
    service = ScholarshipService(ScholarshipRepository(db))
    rows = await service.list_scholarships(skip=skip, limit=limit)
    return [ScholarshipOut.model_validate(row) for row in rows]


@router.get("/search", response_model=list[ScholarshipOut])
async def search_scholarships(
    country: str | None = Query(default=None),
    level: str | None = Query(default=None),
    field_of_study: str | None = Query(default=None),
    deadline_before: date | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(db_session_dependency),
) -> list[ScholarshipOut]:
    service = ScholarshipService(ScholarshipRepository(db))
    rows = await service.search_scholarships(
        country=country,
        level=level,
        field_of_study=field_of_study,
        deadline_before=deadline_before,
        skip=skip,
        limit=limit,
    )
    return [ScholarshipOut.model_validate(row) for row in rows]


@router.get("/{scholarship_id}", response_model=ScholarshipOut)
async def scholarship_detail(scholarship_id: int, db: AsyncSession = Depends(db_session_dependency)) -> ScholarshipOut:
    service = ScholarshipService(ScholarshipRepository(db))
    row = await service.get_detail(scholarship_id)
    return ScholarshipOut.model_validate(row)
