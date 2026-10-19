from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.aircraft import router as aircraft_router
from backend.routes.chat import router as chat_router


app = FastAPI(
    title="AeroMind API",
    description="Interactive Aircraft Intelligence Lab",
    version="0.1.0",
)

# Allow the local Vite development server to call the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "project": "AeroMind"}


app.include_router(aircraft_router)
app.include_router(chat_router)
