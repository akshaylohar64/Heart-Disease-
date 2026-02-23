from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np
import os

app = FastAPI(title="Heart Disease Prediction API")

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "model", "model_output.pkl")
MODEL_PATH = os.path.abspath(MODEL_PATH)

model = joblib.load(MODEL_PATH)

class PatientInput(BaseModel):
    age: float
    sex: float
    chest_pain_type: float
    resting_bp: float
    cholesterol: float
    fasting_blood_sugar: float
    resting_ecg: float
    max_heart_rate: float
    exercise_induced_angina: float
    st_depression: float
    st_slope: float
    num_major_vessels: float
    thalassemia: float

@app.get("/")
def home():
    return {"message": "Heart Disease API is running!"}

@app.post("/predict")
def predict(data: PatientInput):
    features = np.array([[
        data.age,
        data.sex,
        data.chest_pain_type,
        data.resting_bp,
        data.cholesterol,
        data.fasting_blood_sugar,
        data.resting_ecg,
        data.max_heart_rate,
        data.exercise_induced_angina,
        data.st_depression,
        data.st_slope,
        data.num_major_vessels,
        data.thalassemia
    ]])

    pred = int(model.predict(features)[0])
    prob = float(model.predict_proba(features)[0][1])

    return {"prediction": pred, "probability": prob}
