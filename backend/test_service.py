from backend.database.connection import SessionLocal
from backend.database.models import Document


db = SessionLocal()

document = db.query(Document).filter(
    Document.id == "a320_ac_0624"
).first()

print(document.id)
print(document.aircraft_id)
print(document.title)
print(document.file_path)
print(document.document_type)

db.close()