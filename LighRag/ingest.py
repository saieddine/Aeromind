import asyncio
import sys
from pathlib import Path
from rag_factory import get_rag

BASE = Path(__file__).resolve().parent.parent  # Airbus folder

async def main(aircraft_id, txt_name):
    rag = await get_rag(aircraft_id)
    path = BASE / "data" / txt_name
    if not path.exists():
        print(f"FILE NOT FOUND: {path}")
        return
    text = path.read_text(encoding="utf-8")
    print(f"Ingesting {len(text)} characters from {path.name} into aircraft_id='{aircraft_id}'...")
    await rag.ainsert(text, file_paths=path.name)
    await rag.finalize_storages()
    print("Ingestion done")

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1], sys.argv[2]))