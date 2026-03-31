import joblib
import os
import pandas as pd

MODEL_PATH = "intelligence/ml_engine/model.pkl"

def predict_student(iat1, iat2=0, iat3=0):
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("Model not trained yet. Run train_model() first.")

    model = joblib.load(MODEL_PATH)

    # fix: pass as DataFrame with column names matching training
    features = pd.DataFrame([[iat1, iat2, iat3]], columns=["iat1", "iat2", "iat3"])

    pred  = model.predict(features)[0]
    proba = model.predict_proba(features)[0][1]

    return {
        "will_fail": bool(pred),
        "risk_probability": round(float(proba), 2),
        "risk_level": "high" if proba > 0.7 else "medium" if proba > 0.4 else "low"
    }