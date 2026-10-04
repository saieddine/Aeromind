from sqlalchemy.orm import Session

from backend.database.models import Aircraft, Component, Document


def get_all_aircraft(db: Session):
    return db.query(Aircraft).all()


def get_aircraft_by_id(db: Session, aircraft_id: str):
    return db.query(Aircraft).filter(
        Aircraft.id == aircraft_id
    ).first()


def get_components_by_aircraft(
    db: Session,
    aircraft_id: str
):
    return db.query(Component).filter(
        Component.aircraft_id == aircraft_id
    ).all()


def get_documents_by_aircraft(
    db: Session,
    aircraft_id: str
):
    return db.query(Document).filter(
        Document.aircraft_id == aircraft_id
    ).all()