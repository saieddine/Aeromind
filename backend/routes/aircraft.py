from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.schemas.aircraft import (
    AircraftResponse,
    ComponentResponse,
    DocumentResponse
)
from backend.services.aircraft_service import (
    get_all_aircraft,
    get_aircraft_by_id as find_aircraft_by_id,
    get_components_by_aircraft,
    get_documents_by_aircraft
)

router = APIRouter(
    prefix="/api/aircraft",
    tags=["Aircraft"]
)


@router.get("", response_model=list[AircraftResponse])
def get_aircraft(db: Session = Depends(get_db)):
    return get_all_aircraft(db)


@router.get("/{aircraft_id}", response_model=AircraftResponse)
def get_aircraft_by_id(
    aircraft_id: str,
    db: Session = Depends(get_db)
):
    aircraft = find_aircraft_by_id(db, aircraft_id)

    if aircraft is None:
        raise HTTPException(
            status_code=404,
            detail="Aircraft not found"
        )

    return aircraft


@router.get(
    "/{aircraft_id}/components",
    response_model=list[ComponentResponse]
)
def get_aircraft_components(
    aircraft_id: str,
    db: Session = Depends(get_db)
):
    aircraft = find_aircraft_by_id(db, aircraft_id)

    if aircraft is None:
        raise HTTPException(
            status_code=404,
            detail="Aircraft not found"
        )

    return get_components_by_aircraft(db, aircraft_id)


@router.get(
    "/{aircraft_id}/documents",
    response_model=list[DocumentResponse]
)
def get_aircraft_documents(
    aircraft_id: str,
    db: Session = Depends(get_db)
):
    aircraft = find_aircraft_by_id(db, aircraft_id)

    if aircraft is None:
        raise HTTPException(
            status_code=404,
            detail="Aircraft not found"
        )

    return get_documents_by_aircraft(db, aircraft_id)
@router.get("/{aircraft_id}", response_model=AircraftResponse)
def get_aircraft(
    aircraft_id: str,
    db: Session = Depends(get_db)
):
    aircraft = get_aircraft_by_id(db, aircraft_id)

    if aircraft is None:
        raise HTTPException(status_code=404, detail="Aircraft not found")

    return aircraft