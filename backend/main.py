import os
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add backend dir to path so imports work
sys.path.insert(0, str(Path(__file__).parent))

from api import services
from api.routes import router


app = FastAPI(title="Invoice & Receipt Processing Platform", version="1.0.0")

frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin, "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def health_check():
    return {"status": "ok", "service": "invoice-platform-backend"}


@app.post("/reset")
def reset_for_validator():
    # Compatibility endpoint for external validator scripts that call /reset.
    return services.reset_environment(batch_size=12)
