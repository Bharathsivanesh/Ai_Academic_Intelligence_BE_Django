from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import os

from .dataset import generate_dataset

def train_model():
    df = generate_dataset()

    if df.empty:
        print("❌ No data available for training")
        return None

    X = df[["iat1", "iat2", "iat3", "avg"]]
    y = df["fail"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    acc = accuracy_score(y_test, predictions)
    print(f"✅ Accuracy: {acc:.2f}")

    # make sure the folder exists before saving
    os.makedirs("intelligence/ml_engine", exist_ok=True)
    joblib.dump(model, "intelligence/ml_engine/model.pkl")
    print("✅ Model saved!")

    return acc