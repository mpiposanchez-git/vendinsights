"""FastAPI application for serving model predictions."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class PredictRequest(BaseModel):
    # define features expected by the model
    feature1: float
    feature2: float
    # add more features as needed

class PredictResponse(BaseModel):
    prediction: float
    probability: float


@app.get("/")
def read_root():
    return {"message": "mps_package API is running"}


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    # placeholder logic
    try:
        # in real code load a model and compute prediction
        pred = 0.0
        prob = 0.0
        return PredictResponse(prediction=pred, probability=prob)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
