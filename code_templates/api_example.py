"""Template: API code for model predictions"""

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Input(BaseModel):
    feature1: float
    feature2: float

@app.post("/predict")
def predict(data: Input):
    # load model and make prediction
    return {"prediction": 0.0}
