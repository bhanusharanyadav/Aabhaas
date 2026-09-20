import os
try:
    import joblib
except ImportError:
    import pickle as joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH_PRIMARY = os.path.join(BASE_DIR, "Dashboard", "models", "trained_model.pkl")
MODEL_PATH_FALLBACK = os.path.join(BASE_DIR, "Models", "random_forest_landslide.pkl")
FEATURE_PATH_PRIMARY = os.path.join(BASE_DIR, "Dashboard", "models", "feature_columns.pkl")
FEATURE_PATH_FALLBACK = os.path.join(BASE_DIR, "Models", "feature_columns.pkl")


def get_risk_category(score: float) -> Tuple[str, str]:
    """
    Returns (category_name, hex_color) for a risk score from 0-100.
    Categories:
    0–20     Very Low
    21–40    Low
    41–60    Moderate
    61–80    High
    81–100   Very High
    """
    score = float(np.clip(score, 0, 100))
    if score <= 20:
        return "Very Low", "#10B981"  # Emerald
    elif score <= 40:
        return "Low", "#3B82F6"       # Blue
    elif score <= 60:
        return "Moderate", "#F59E0B"  # Amber
    elif score <= 80:
        return "High", "#EF4444"      # Red
    else:
        return "Very High", "#8B5CF6"  # Purple/Dark Red


class LandslideRiskEngine:
    def __init__(self):
        self.model = None
        self.feature_columns = []
        self.has_ml_model = False
        self._load_model()

    def _load_model(self):
        """Loads trained Random Forest classifier if available."""
        model_file = None
        if os.path.exists(MODEL_PATH_PRIMARY):
            model_file = MODEL_PATH_PRIMARY
        elif os.path.exists(MODEL_PATH_FALLBACK):
            model_file = MODEL_PATH_FALLBACK

        feat_file = None
        if os.path.exists(FEATURE_PATH_PRIMARY):
            feat_file = FEATURE_PATH_PRIMARY
        elif os.path.exists(FEATURE_PATH_FALLBACK):
            feat_file = FEATURE_PATH_FALLBACK

        if model_file and feat_file:
            try:
                self.model = joblib.load(model_file)
                self.feature_columns = joblib.load(feat_file)
                self.has_ml_model = True
            except Exception:
                self.has_ml_model = False
        else:
            self.has_ml_model = False

    def compute_rule_based_risk(self, row: pd.Series) -> Dict[str, Any]:
        """
        Calculates a transparent 0-100 Rule-based Environmental Risk Index.
        Does NOT claim to be AI; strictly labeled as 'Rule-based environmental risk index'.
        """
        # 1. Soil Water sub-score (0 - 100)
        swvl1 = row.get("swvl1", 0.25)
        if pd.isna(swvl1):
            swvl1 = 0.25
        soil_score = min(100.0, max(0.0, (swvl1 / 0.50) * 100))

        # 2. Rainfall sub-score (antecedent rainfall windows or tcrw)
        rain_72h = row.get("rain_72h", row.get("rainfall_mm", row.get("total_column_rain_water", 0.0)))
        if pd.isna(rain_72h):
            rain_72h = 0.0
        rain_score = min(100.0, max(0.0, (rain_72h / 150.0) * 100))

        # 3. Humidity & Moisture saturation sub-score
        rh = row.get("relative_humidity", 70.0)
        if pd.isna(rh):
            rh = 70.0
        humidity_score = min(100.0, max(0.0, ((rh - 40) / 60) * 100))

        # 4. Temperature & Pressure stability factor
        temp = row.get("temperature_c", 20.0)
        if pd.isna(temp):
            temp = 20.0
        # Warm air holds more moisture, rapid freeze-thaw or intense heat can destabilize
        temp_score = min(100.0, max(0.0, (temp / 35.0) * 50))

        # Combined Weighted Index:
        # Rain: 40%, Soil Water: 35%, Humidity: 15%, Temp: 10%
        total_risk = (rain_score * 0.40) + (soil_score * 0.35) + (humidity_score * 0.15) + (temp_score * 0.10)
        total_risk = float(np.clip(total_risk, 0, 100))

        cat, color = get_risk_category(total_risk)

        return {
            "risk_score": round(total_risk, 1),
            "category": cat,
            "color": color,
            "model_type": "Rule-based environmental risk index",
            "breakdown": {
                "Rainfall Contribution": round(rain_score * 0.40, 1),
                "Soil Moisture Contribution": round(soil_score * 0.35, 1),
                "Humidity Contribution": round(humidity_score * 0.15, 1),
                "Temperature Factor": round(temp_score * 0.10, 1)
            }
        }

    def predict_risk(self, row: pd.Series) -> Dict[str, Any]:
        """
        Computes ML-based landslide prediction probability if model is loaded,
        otherwise defaults to rule-based environmental risk index.
        """
        if self.has_ml_model and self.model is not None:
            try:
                # Prepare feature vector matching self.feature_columns
                feat_dict = {}
                for col in self.feature_columns:
                    val = row.get(col, np.nan)
                    if pd.isna(val):
                        # Fill default average values if missing
                        if "rain" in col or "tp" in col:
                            val = 0.0
                        elif "swvl" in col:
                            val = 0.25
                        elif "temp" in col or "t2m" in col:
                            val = 18.0
                        elif "dew" in col or "d2m" in col:
                            val = 14.0
                        elif "wind" in col:
                            val = 3.5
                        elif "sp" in col:
                            val = 98000.0
                        else:
                            val = 0.0
                    feat_dict[col] = [float(val)]

                X_input = pd.DataFrame(feat_dict)
                proba = float(self.model.predict_proba(X_input)[0][1])
                score = round(proba * 100.0, 1)
                cat, color = get_risk_category(score)

                # Feature importances breakdown
                importances = self.model.feature_importances_
                breakdown = {}
                for col, imp in zip(self.feature_columns, importances):
                    breakdown[col.replace("_", " ").title()] = round(float(imp * score), 1)

                # Group top contributors
                top_breakdown = dict(sorted(breakdown.items(), key=lambda x: x[1], reverse=True)[:5])

                return {
                    "risk_score": score,
                    "probability": round(proba, 4),
                    "category": cat,
                    "color": color,
                    "model_type": "ML-based landslide probability",
                    "breakdown": top_breakdown
                }
            except Exception:
                pass

        # Fallback if ML prediction fails or model not loaded
        return self.compute_rule_based_risk(row)


# Global singleton instance
risk_engine = LandslideRiskEngine()
