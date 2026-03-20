"""
Hooke's Law Neural Network — FastAPI application

Run:
    cd week2/LinRegSpr
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

or simply:
    python main.py
"""

import os
import json
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
import uvicorn

# ── Ensure we run from this file's directory ─────────────────────────────────
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from model import SpringModel

logging.basicConfig(level=logging.INFO, format="%(levelname)s │ %(message)s")
log = logging.getLogger(__name__)

# ── State ────────────────────────────────────────────────────────────────────
spring_model: SpringModel | None = None


# ── Lifespan (startup / shutdown) ────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    global spring_model
    log.info("Training HooksLawNet …")
    spring_model = SpringModel(k=50.0, g=9.81, noise_std=0.003, seed=42)
    spring_model.train(epochs=500)
    spring_model.save_plots()
    info = spring_model.get_info()
    log.info(
        f"Training complete  │  epochs={info['epochs_run']}"
        f"  │  MAE={info['final_mae']*1000:.4f} mm"
        f"  │  params={info['model_params']:,}"
    )
    yield
    log.info("Shutting down …")


# ── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Hooke's Law — TensorFlow Spring Model",
    description="Neural network that learns F = kx and predicts spring elongation.",
    version="1.0.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/output", StaticFiles(directory="output"), name="output")
templates = Jinja2Templates(directory="templates")


# ── Schemas ──────────────────────────────────────────────────────────────────
class PredictRequest(BaseModel):
    mass: float = Field(..., gt=0, le=100, description="Mass in kilograms")


class PredictResponse(BaseModel):
    mass: float
    elongation_m: float
    elongation_cm: float
    theoretical_m: float
    theoretical_cm: float
    error_pct: float


# ── Routes ───────────────────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/predict", response_model=PredictResponse, tags=["Inference"])
async def predict(body: PredictRequest):
    """Return the predicted spring elongation for a given mass."""
    if spring_model is None:
        raise HTTPException(503, "Model not ready yet.")
    elong   = spring_model.predict(body.mass)
    theory  = (body.mass * spring_model.g) / spring_model.k
    err_pct = abs(elong - theory) / max(theory, 1e-9) * 100.0
    return PredictResponse(
        mass          = body.mass,
        elongation_m  = round(elong,   6),
        elongation_cm = round(elong * 100, 4),
        theoretical_m = round(theory,  6),
        theoretical_cm= round(theory * 100, 4),
        error_pct     = round(err_pct, 4),
    )


@app.get("/api/model-info", tags=["Model"])
async def model_info():
    """Return architecture and final training metrics."""
    if spring_model is None:
        raise HTTPException(503, "Model not ready.")
    return JSONResponse(spring_model.get_info())


@app.get("/api/history", tags=["Model"])
async def training_history():
    """Return per-epoch loss / MAE history (for interactive charts)."""
    path = os.path.join("output", "training_history.json")
    if not os.path.exists(path):
        raise HTTPException(404, "History not found.")
    with open(path) as f:
        return JSONResponse(json.load(f))


@app.get("/api/health", tags=["System"])
async def health():
    return {"status": "ok", "model_ready": spring_model is not None}


# ── Entry-point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
