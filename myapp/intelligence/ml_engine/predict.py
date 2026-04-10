import os
import joblib
import pandas as pd

MODEL_PATH = "intelligence/ml_engine/model.pkl"

def predict_student(iat1, iat2=0, iat3=0):
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("Model not trained yet. Run train_model() first.")

    model = joblib.load(MODEL_PATH)

    avg = (iat1 + iat2 + iat3) / 3

    features = pd.DataFrame(
        [[iat1, iat2, iat3, avg]],
        columns=["iat1", "iat2", "iat3", "avg"]
    )

    pred      = model.predict(features)[0]
    classes   = list(model.classes_)
    proba_raw = model.predict_proba(features)[0]
    proba     = proba_raw[classes.index(1)] if 1 in classes else 0.0

    return {
        "will_fail":        bool(pred),
        "risk_probability": round(float(proba), 2),
        "risk_level":       "high" if proba > 0.7 else "medium" if proba > 0.4 else "low"
    }