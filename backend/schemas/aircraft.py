from pydantic import BaseModel


class AircraftResponse(BaseModel):
    id: str
    manufacturer: str
    model: str
    description: str | None = None


class ComponentResponse(BaseModel):
    id: str
    aircraft_id: str
    name: str
    type: str
    description: str | None = None


class DocumentResponse(BaseModel):
    id: str
    aircraft_id: str
    title: str
    file_path: str
    document_type: str