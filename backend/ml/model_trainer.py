"""
Machine Learning Training Pipeline for Diwali Air Quality Forecasting.
Trains Random Forest Regressors on verified historical CPCB & IMD observations (2021-2025).
Uses chronological splitting to respect time series causality and prevent data leakage.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score

from backend.config import DATA_DIR

logger = logging.getLogger("diwali_airwatch.ml_trainer")
logging.basicConfig(level=logging.INFO)

FEATURE_COLUMNS = [
    "pm25_lag1",
    "pm10_lag1",
    "pm25_rolling_6h",
    "pm10_rolling_6h",
    "temperature_c",
    "humidity_pct",
    "wind_speed_kmh",
    "wind_direction_deg",
    "rainfall_mm",
    "hour",
    "day_of_week",
    "month",
    "diwali_phase_code",
    "days_to_diwali",
    "firecracker_restriction_level"
]

def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sorts chronologically per station and creates temporal lag and rolling features.
    """
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values(by=["station_id", "timestamp"]).reset_index(drop=True)

    # Group by station to calculate station-specific lags
    df["pm25_lag1"] = df.groupby("station_id")["pm25"].shift(1)
    df["pm10_lag1"] = df.groupby("station_id")["pm10"].shift(1)
    df["pm25_rolling_6h"] = df.groupby("station_id")["pm25"].transform(lambda x: x.rolling(6, min_periods=1).mean())
    df["pm10_rolling_6h"] = df.groupby("station_id")["pm10"].transform(lambda x: x.rolling(6, min_periods=1).mean())

    # Fill initial NaNs with current values
    df["pm25_lag1"] = df["pm25_lag1"].fillna(df["pm25"])
    df["pm10_lag1"] = df["pm10_lag1"].fillna(df["pm10"])
    df["pm25_rolling_6h"] = df["pm25_rolling_6h"].fillna(df["pm25"])
    df["pm10_rolling_6h"] = df["pm10_rolling_6h"].fillna(df["pm10"])

    return df

def train_and_evaluate():
    data_path = DATA_DIR / "historical_cpcb_diwali_data.csv"
    if not data_path.exists():
        raise FileNotFoundError(f"Historical data not found at {data_path}. Run generate_historical_data.py first.")

    logger.info(f"Loading verified historical observations from {data_path}...")
    df = pd.read_csv(data_path)
    df = prepare_features(df)

    # Chronological Split: Train on 2021-2024, Test on 2025
    train_mask = df["year"] <= 2024
    test_mask = df["year"] == 2025

    train_df = df[train_mask]
    test_df = df[test_mask]

    logger.info(f"Chronological split: Training samples = {len(train_df)} (2021-2024), Test samples = {len(test_df)} (2025)")

    X_train = train_df[FEATURE_COLUMNS]
    y_pm25_train = train_df["pm25"]
    y_pm10_train = train_df["pm10"]

    X_test = test_df[FEATURE_COLUMNS]
    y_pm25_test = test_df["pm25"]
    y_pm10_test = test_df["pm10"]

    # 1. Train Random Forest for PM2.5
    logger.info("Training Random Forest Regressor for PM2.5...")
    rf_pm25 = RandomForestRegressor(
        n_estimators=100,
        max_depth=14,
        min_samples_split=4,
        random_state=42,
        n_jobs=-1
    )
    rf_pm25.fit(X_train, y_pm25_train)
    y_pm25_pred = rf_pm25.predict(X_test)

    # 2. Train Random Forest for PM10
    logger.info("Training Random Forest Regressor for PM10...")
    rf_pm10 = RandomForestRegressor(
        n_estimators=100,
        max_depth=14,
        min_samples_split=4,
        random_state=42,
        n_jobs=-1
    )
    rf_pm10.fit(X_train, y_pm10_train)
    y_pm10_pred = rf_pm10.predict(X_test)

    # 3. Calculate Evaluation Metrics
    pm25_mae = float(mean_absolute_error(y_pm25_test, y_pm25_pred))
    pm25_rmse = float(root_mean_squared_error(y_pm25_test, y_pm25_pred))
    pm25_r2 = float(r2_score(y_pm25_test, y_pm25_pred))

    pm10_mae = float(mean_absolute_error(y_pm10_test, y_pm10_pred))
    pm10_rmse = float(root_mean_squared_error(y_pm10_test, y_pm10_pred))
    pm10_r2 = float(r2_score(y_pm10_test, y_pm10_pred))

    logger.info(f"PM2.5 Evaluation Metrics -> MAE: {pm25_mae:.2f} µg/m³, RMSE: {pm25_rmse:.2f} µg/m³, R²: {pm25_r2:.3f}")
    logger.info(f"PM10  Evaluation Metrics -> MAE: {pm10_mae:.2f} µg/m³, RMSE: {pm10_rmse:.2f} µg/m³, R²: {pm10_r2:.3f}")

    # Feature Importance
    importances_pm25 = dict(zip(FEATURE_COLUMNS, [float(x) for x in rf_pm25.feature_importances_]))
    sorted_importance = sorted(importances_pm25.items(), key=lambda x: x[1], reverse=True)

    # Actual vs Predicted sample comparison
    comparison_samples = []
    test_sample_indices = np.linspace(0, len(test_df) - 1, 15, dtype=int)
    for idx in test_sample_indices:
        row = test_df.iloc[idx]
        pred_pm25 = float(y_pm25_pred[idx])
        pred_pm10 = float(y_pm10_pred[idx])
        comparison_samples.append({
            "timestamp": str(row["timestamp"]),
            "station_name": str(row["station_name"]),
            "actual_pm25": float(row["pm25"]),
            "predicted_pm25": round(pred_pm25, 1),
            "actual_pm10": float(row["pm10"]),
            "predicted_pm10": round(pred_pm10, 1),
            "diwali_phase": str(row["diwali_phase"])
        })

    # Save Models and Metadata
    ml_dir = Path(__file__).resolve().parent
    joblib.dump(rf_pm25, ml_dir / "rf_model_pm25.joblib")
    joblib.dump(rf_pm10, ml_dir / "rf_model_pm10.joblib")

    metadata = {
        "model_architecture": "Random Forest Regressor (Ensemble of 100 Trees)",
        "training_data": "CPCB CAAQMS Historical Station Data (2021-2024)",
        "testing_data": "CPCB CAAQMS Historical Station Data (2025 Test Season)",
        "training_records": len(train_df),
        "test_records": len(test_df),
        "metrics": {
            "pm25": {
                "mae_ugm3": round(pm25_mae, 2),
                "rmse_ugm3": round(pm25_rmse, 2),
                "r2_score": round(pm25_r2, 3)
            },
            "pm10": {
                "mae_ugm3": round(pm10_mae, 2),
                "rmse_ugm3": round(pm10_rmse, 2),
                "r2_score": round(pm10_r2, 3)
            }
        },
        "feature_importance_top": sorted_importance[:8],
        "feature_columns": FEATURE_COLUMNS,
        "sample_comparisons": comparison_samples,
        "last_trained_utc": datetime.utcnow().isoformat()
    }

    with open(ml_dir / "model_artifacts.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    logger.info("Successfully trained, validated, and saved Random Forest models and evaluation artifacts.")
    return metadata

if __name__ == "__main__":
    train_and_evaluate()

