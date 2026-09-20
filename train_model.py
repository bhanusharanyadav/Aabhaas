import os
import pandas as pd
import joblib
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
    ConfusionMatrixDisplay
)

# ============================================================
# AABHAAS - ML MODEL TRAINING
# ============================================================

FILE = r"DATA\Raw\Landslide event\processed\labeled\labeled_with_rainfall_features.csv"

MODEL_DIR = "Models"

os.makedirs(MODEL_DIR, exist_ok=True)

print("=" * 70)
print("AABHAAS - HYBRID AI LANDSLIDE PREDICTION")
print("=" * 70)

# ------------------------------------------------------------
# LOAD DATA
# ------------------------------------------------------------

df = pd.read_csv(FILE)

print("\nDataset:")
print("Rows:", len(df))
print("Columns:", len(df.columns))

# ------------------------------------------------------------
# FEATURES
# ------------------------------------------------------------

features = [
    "rainfall_mm",
    "rain_3h",
    "rain_6h",
    "rain_12h",
    "rain_24h",
    "rain_72h",
    "temperature_c",
    "dewpoint_c",
    "wind_speed",
    "sp",
    "swvl1",
    "swvl2",
    "swvl3",
    "swvl4",
    "lai_lv",
    "lai_hv",
    "cvl",
    "cvh"
]

target = "landslide"

data = df[features + [target]].copy()

# Remove incomplete rainfall windows
data = data.dropna()

print("\nClean ML dataset:")
print("Rows:", len(data))
print("Positive:", int((data[target] == 1).sum()))
print("Negative:", int((data[target] == 0).sum()))

X = data[features]
y = data[target]

# ------------------------------------------------------------
# TRAIN / TEST SPLIT
# ------------------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nTrain rows:", len(X_train))
print("Test rows :", len(X_test))

# ============================================================
# RANDOM FOREST
# ============================================================

rf = RandomForestClassifier(
    n_estimators=300,
    max_depth=8,
    min_samples_leaf=3,
    class_weight="balanced",
    random_state=42
)

rf.fit(X_train, y_train)

rf_pred = rf.predict(X_test)

accuracy = accuracy_score(y_test, rf_pred)
precision = precision_score(y_test, rf_pred, zero_division=0)
recall = recall_score(y_test, rf_pred, zero_division=0)
f1 = f1_score(y_test, rf_pred, zero_division=0)

print("\n" + "=" * 70)
print("RANDOM FOREST RESULTS")
print("=" * 70)

print("Accuracy :", round(accuracy, 4))
print("Precision:", round(precision, 4))
print("Recall   :", round(recall, 4))
print("F1 Score :", round(f1, 4))

cm = confusion_matrix(y_test, rf_pred)

print("\nConfusion Matrix:")
print(cm)

print("\nClassification Report:")
print(classification_report(y_test, rf_pred, zero_division=0))

# ------------------------------------------------------------
# SAVE RANDOM FOREST
# ------------------------------------------------------------

model_path = os.path.join(
    MODEL_DIR,
    "random_forest_landslide.pkl"
)

joblib.dump(rf, model_path)

print("\nRandom Forest saved:")
print(model_path)

# ------------------------------------------------------------
# SAVE FEATURE LIST
# ------------------------------------------------------------

feature_path = os.path.join(
    MODEL_DIR,
    "feature_columns.pkl"
)

joblib.dump(features, feature_path)

print("Feature list saved:")
print(feature_path)

# ============================================================
# FEATURE IMPORTANCE
# ============================================================

importance = pd.DataFrame({
    "feature": features,
    "importance": rf.feature_importances_
}).sort_values(
    "importance",
    ascending=False
)

print("\nFeature Importance:")
print(importance.to_string(index=False))

# Save feature importance
importance.to_csv(
    os.path.join(
        MODEL_DIR,
        "feature_importance.csv"
    ),
    index=False
)

# ------------------------------------------------------------
# FEATURE IMPORTANCE PLOT
# ------------------------------------------------------------

plt.figure(figsize=(10, 7))

plt.barh(
    importance["feature"],
    importance["importance"]
)

plt.xlabel("Importance")
plt.ylabel("Feature")
plt.title("AABHAAS - Random Forest Feature Importance")

plt.gca().invert_yaxis()

plt.tight_layout()

plt.savefig(
    os.path.join(
        MODEL_DIR,
        "feature_importance.png"
    ),
    dpi=300
)

plt.close()

print("\nFeature importance plot saved.")

# ============================================================
# CONFUSION MATRIX PLOT
# ============================================================

disp = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=["No Landslide", "Landslide"]
)

fig, ax = plt.subplots(figsize=(6, 6))

disp.plot(ax=ax)

plt.title("AABHAAS - Random Forest Confusion Matrix")

plt.tight_layout()

plt.savefig(
    os.path.join(
        MODEL_DIR,
        "confusion_matrix.png"
    ),
    dpi=300
)

plt.close()

print("Confusion matrix plot saved.")

# ============================================================
# LOGISTIC REGRESSION BASELINE
# ============================================================

lr = Pipeline([
    ("scaler", StandardScaler()),
    ("model", LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        random_state=42
    ))
])

lr.fit(X_train, y_train)

lr_pred = lr.predict(X_test)

print("\n" + "=" * 70)
print("LOGISTIC REGRESSION BASELINE")
print("=" * 70)

print(
    "Accuracy :",
    round(accuracy_score(y_test, lr_pred), 4)
)

print(
    "Precision:",
    round(precision_score(y_test, lr_pred, zero_division=0), 4)
)

print(
    "Recall   :",
    round(recall_score(y_test, lr_pred, zero_division=0), 4)
)

print(
    "F1 Score :",
    round(f1_score(y_test, lr_pred, zero_division=0), 4)
)

# ============================================================
# DEMO PREDICTION
# ============================================================

sample = X_test.iloc[[0]]

probability = rf.predict_proba(sample)[0][1]

print("\n" + "=" * 70)
print("AABHAAS DEMO PREDICTION")
print("=" * 70)

print(
    "Landslide probability:",
    round(probability * 100, 2),
    "%"
)

if probability < 0.30:
    risk = "LOW"
elif probability < 0.70:
    risk = "MODERATE"
else:
    risk = "HIGH"

print("Risk Level:", risk)

print("\n" + "=" * 70)
print("AABHAAS MODEL TRAINING COMPLETE")
print("=" * 70)