"""
Train and export the ML artifacts needed by the app:
 - model.pkl  (RandomForestClassifier)
 - scaler.pkl (StandardScaler)

Usage:
  python train_model.py

Assumes heart.csv is present in the project root.
"""

from __future__ import annotations

import pickle
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "heart.csv"
MODEL_PATH = ROOT / "model.pkl"
SCALER_PATH = ROOT / "scaler.pkl"


def main() -> None:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Missing dataset: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)
    if "target" not in df.columns:
        raise ValueError("heart.csv must include a 'target' column.")

    X = df.drop("target", axis=1)
    y = df["target"]

    X_train, _X_test, y_train, _y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train_scaled, y_train)

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    with open(SCALER_PATH, "wb") as f:
        pickle.dump(scaler, f)

    print(f"✅ Wrote {MODEL_PATH.name} and {SCALER_PATH.name} to {ROOT}")


if __name__ == "__main__":
    main()


