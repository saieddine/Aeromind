from fastapi import FastAPI

from backend.routes.aircraft import router as aircraft_router
from backend.routes.chat import router as chat_router


app = FastAPI(
    title="AeroMind API",
    description="Interactive Aircraft Intelligence Lab",
    version="0.1.0",
)


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "project": "AeroMind",
    }


app.include_router(aircraft_router)
app.include_router(chat_router)
