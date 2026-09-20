import os
import joblib
import pandas as pd

# ============================================================
# AABHAAS - LANDSLIDE PREDICTION ENGINE
# ============================================================

MODEL_PATH = r"Models\random_forest_landslide.pkl"
FEATURE_PATH = r"Models\feature_columns.pkl"

# Load trained model
model = joblib.load(MODEL_PATH)

# Load feature names
features = joblib.load(FEATURE_PATH)


def predict_landslide(input_data):
    """
    input_data must contain all features used during training.
    Returns probability and risk level.
    """

    # Convert input to DataFrame
    data = pd.DataFrame([input_data])

    # Make sure feature order is exactly the same
    data = data[features]

    # Predict probability
    probability = model.predict_proba(data)[0][1]

    # Prototype risk classification
    if probability < 0.30:
        risk = "LOW"
    elif probability < 0.70:
        risk = "MODERATE"
    else:
        risk = "HIGH"

    return probability, risk


# ============================================================
# TEST PREDICTION
# ============================================================

if __name__ == "__main__":

    sample = {
        "rainfall_mm": 2.0,
        "rain_3h": 4.0,
        "rain_6h": 7.0,
        "rain_12h": 10.0,
        "rain_24h": 15.0,
        "rain_72h": 30.0,
        "temperature_c": 23.0,
        "dewpoint_c": 20.0,
        "wind_speed": 1.5,
        "sp": 85000.0,
        "swvl1": 0.42,
        "swvl2": 0.41,
        "swvl3": 0.40,
        "swvl4": 0.39,
        "lai_lv": 2.85,
        "lai_hv": 2.43,
        "cvl": 0.44,
        "cvh": 0.56
    }

    probability, risk = predict_landslide(sample)

    print("=" * 60)
    print("AABHAAS - LANDSLIDE PREDICTION")
    print("=" * 60)

    print("Probability:", round(probability * 100, 2), "%")
    print("Risk Level :", risk)

    print("=" * 60)