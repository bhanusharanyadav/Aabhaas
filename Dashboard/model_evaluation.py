import os
import numpy as np
import pandas as pd
try:
    import plotly.express as px
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False
    px = None
    go = None
from typing import Dict, Any, Tuple

try:
    from sklearn.metrics import (
        accuracy_score,
        precision_score,
        recall_score,
        f1_score,
        roc_auc_score,
        confusion_matrix,
        roc_curve,
        precision_recall_curve
    )
except ImportError:
    # Pure NumPy metric fallbacks if sklearn is not installed
    def accuracy_score(y_true, y_pred):
        y_true, y_pred = np.array(y_true), np.array(y_pred)
        return float(np.mean(y_true == y_pred))

    def precision_score(y_true, y_pred, zero_division=0):
        y_true, y_pred = np.array(y_true), np.array(y_pred)
        tp = np.sum((y_true == 1) & (y_pred == 1))
        fp = np.sum((y_true == 0) & (y_pred == 1))
        return float(tp / (tp + fp)) if (tp + fp) > 0 else float(zero_division)

    def recall_score(y_true, y_pred, zero_division=0):
        y_true, y_pred = np.array(y_true), np.array(y_pred)
        tp = np.sum((y_true == 1) & (y_pred == 1))
        fn = np.sum((y_true == 1) & (y_pred == 0))
        return float(tp / (tp + fn)) if (tp + fn) > 0 else float(zero_division)

    def f1_score(y_true, y_pred, zero_division=0):
        p = precision_score(y_true, y_pred, zero_division)
        r = recall_score(y_true, y_pred, zero_division)
        return float(2 * p * r / (p + r)) if (p + r) > 0 else float(zero_division)

    def confusion_matrix(y_true, y_pred, labels=[0, 1]):
        y_true, y_pred = np.array(y_true), np.array(y_pred)
        tn = np.sum((y_true == 0) & (y_pred == 0))
        fp = np.sum((y_true == 0) & (y_pred == 1))
        fn = np.sum((y_true == 1) & (y_pred == 0))
        tp = np.sum((y_true == 1) & (y_pred == 1))
        return np.array([[tn, fp], [fn, tp]])

    def roc_auc_score(y_true, y_proba):
        y_true, y_proba = np.array(y_true), np.array(y_proba)
        pos = y_proba[y_true == 1]
        neg = y_proba[y_true == 0]
        if len(pos) == 0 or len(neg) == 0:
            return 0.5
        count = 0.0
        for p in pos:
            count += np.sum(p > neg) + 0.5 * np.sum(p == neg)
        return float(count / (len(pos) * len(neg)))

    def roc_curve(y_true, y_proba):
        thresholds = np.linspace(1.0, 0.0, 50)
        tpr_list, fpr_list = [], []
        y_true = np.array(y_true)
        y_proba = np.array(y_proba)
        for th in thresholds:
            y_p = (y_proba >= th).astype(int)
            tpr_list.append(recall_score(y_true, y_p))
            fp = np.sum((y_true == 0) & (y_p == 1))
            tn = np.sum((y_true == 0) & (y_p == 0))
            fpr_list.append(fp / (fp + tn) if (fp + tn) > 0 else 0.0)
        return fpr_list, tpr_list, thresholds

    def precision_recall_curve(y_true, y_proba):
        thresholds = np.linspace(0.0, 1.0, 50)
        prec_list, rec_list = [], []
        y_true = np.array(y_true)
        y_proba = np.array(y_proba)
        for th in thresholds:
            y_p = (y_proba >= th).astype(int)
            prec_list.append(precision_score(y_true, y_p))
            rec_list.append(recall_score(y_true, y_p))
        return prec_list, rec_list, thresholds

from risk_model import risk_engine


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LABELED_FILE = os.path.join(
    BASE_DIR,
    "DATA",
    "Raw",
    "Landslide event",
    "processed",
    "labeled",
    "labeled_with_rainfall_features.csv"
)
FALLBACK_LABELED = os.path.join(
    BASE_DIR,
    "DATA",
    "Raw",
    "Landslide event",
    "processed",
    "labeled",
    "initial_landslide_labeled_dataset.csv"
)


def load_labeled_ground_truth() -> pd.DataFrame:
    """Loads actual historical ground-truth landslide event labels dataset."""
    path = LABELED_FILE if os.path.exists(LABELED_FILE) else FALLBACK_LABELED
    if os.path.exists(path):
        try:
            df = pd.read_csv(path)
            if "time" in df.columns:
                df["time"] = pd.to_datetime(df["time"])
            return df
        except Exception:
            pass
    return pd.DataFrame()


def evaluate_model_performance(df_labeled: pd.DataFrame = None) -> Dict[str, Any]:
    """
    Evaluates ML model against ground-truth landslide labels using scikit-learn metrics.
    Returns metrics dictionary, confusion matrix, ROC curve, and PR curve data.
    """
    if df_labeled is None or df_labeled.empty:
        df_labeled = load_labeled_ground_truth()

    if df_labeled.empty or "landslide" not in df_labeled.columns:
        return {
            "has_data": False,
            "message": "Historical ground-truth landslide labels are not available, therefore prediction accuracy cannot be calculated from the current dataset."
        }

    target_col = "landslide"
    y_true = df_labeled[target_col].dropna().values

    # If ML model is loaded, get actual model predictions
    if risk_engine.has_ml_model and risk_engine.model is not None:
        try:
            X = df_labeled[risk_engine.feature_columns].fillna(0)
            y_pred = risk_engine.model.predict(X)
            y_proba = risk_engine.model.predict_proba(X)[:, 1]
            model_name = "Random Forest ML Classifier"
        except Exception:
            # Fallback prediction if missing features
            y_pred = (df_labeled.get("rain_72h", 0) > 30).astype(int).values
            y_proba = np.clip(df_labeled.get("rain_72h", 0) / 100.0, 0, 1).values
            model_name = "Rule-based Environmental Threshold Index"
    else:
        # Rule based prediction
        y_pred = (df_labeled.get("rain_72h", 0) > 30).astype(int).values
        y_proba = np.clip(df_labeled.get("rain_72h", 0) / 100.0, 0, 1).values
        model_name = "Rule-based Environmental Threshold Index"

    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)

    try:
        auc = roc_auc_score(y_true, y_proba)
    except Exception:
        auc = 0.5

    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel() if cm.shape == (2, 2) else (0, 0, 0, 0)

    # ROC curve calculations
    fpr, tpr, _ = roc_curve(y_true, y_proba)
    # PR curve calculations
    precision_curve, recall_curve, _ = precision_recall_curve(y_true, y_proba)

    return {
        "has_data": True,
        "model_name": model_name,
        "total_samples": len(y_true),
        "positive_samples": int(sum(y_true == 1)),
        "negative_samples": int(sum(y_true == 0)),
        "accuracy": round(float(acc), 4),
        "precision": round(float(prec), 4),
        "recall": round(float(rec), 4),
        "f1_score": round(float(f1), 4),
        "roc_auc": round(float(auc), 4),
        "confusion_matrix": cm,
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
        "fpr": fpr.tolist() if hasattr(fpr, "tolist") else list(fpr),
        "tpr": tpr.tolist() if hasattr(tpr, "tolist") else list(tpr),
        "precision_curve": precision_curve.tolist() if hasattr(precision_curve, "tolist") else list(precision_curve),
        "recall_curve": recall_curve.tolist() if hasattr(recall_curve, "tolist") else list(recall_curve)
    }


def create_confusion_matrix_figure(eval_dict: Dict[str, Any]) -> go.Figure:
    """Generates an interactive Plotly confusion matrix heatmap."""
    z = [[eval_dict["tn"], eval_dict["fp"]],
         [eval_dict["fn"], eval_dict["tp"]]]

    x_labels = ["Predicted: No Event", "Predicted: Landslide"]
    y_labels = ["Actual: No Event", "Actual: Landslide"]

    fig = px.imshow(
        z,
        x=x_labels,
        y=y_labels,
        color_continuous_scale="Blues",
        text_auto=True,
        title="<b>Interactive Confusion Matrix</b>"
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E2E8F0"),
        height=380
    )
    return fig


def create_roc_curve_figure(eval_dict: Dict[str, Any]) -> go.Figure:
    """Generates ROC Curve figure using Plotly."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=eval_dict["fpr"],
        y=eval_dict["tpr"],
        mode="lines",
        name=f"ROC Curve (AUC = {eval_dict['roc_auc']:.2f})",
        line=dict(color="#3B82F6", width=3)
    ))
    fig.add_trace(go.Scatter(
        x=[0, 1],
        y=[0, 1],
        mode="lines",
        name="Random Classifier Baseline",
        line=dict(color="#94A3B8", dash="dash")
    ))
    fig.update_layout(
        title="<b>Receiver Operating Characteristic (ROC) Curve</b>",
        xaxis_title="False Positive Rate (1 - Specificity)",
        yaxis_title="True Positive Rate (Recall / Sensitivity)",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E2E8F0"),
        height=380
    )
    return fig


def create_pr_curve_figure(eval_dict: Dict[str, Any]) -> go.Figure:
    """Generates Precision-Recall Curve figure using Plotly."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=eval_dict["recall_curve"],
        y=eval_dict["precision_curve"],
        mode="lines",
        name="Precision-Recall Curve",
        line=dict(color="#10B981", width=3)
    ))
    fig.update_layout(
        title="<b>Precision-Recall Curve</b>",
        xaxis_title="Recall (Sensitivity)",
        yaxis_title="Precision (Positive Predictive Value)",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E2E8F0"),
        height=380
    )
    return fig


def evaluate_temporal_performance(df_labeled: pd.DataFrame = None, group_by: str = "Month") -> pd.DataFrame:
    """Evaluates F1 score, precision, and recall over time (Month / Season / Year)."""
    if df_labeled is None or df_labeled.empty:
        df_labeled = load_labeled_ground_truth()

    if df_labeled.empty or "time" not in df_labeled.columns or "landslide" not in df_labeled.columns:
        return pd.DataFrame()

    df = df_labeled.copy()
    df["time"] = pd.to_datetime(df["time"])

    if group_by == "Month":
        df["period"] = df["time"].dt.to_period("M").astype(str)
    elif group_by == "Season":
        # Monsoon (Jun-Sep), Post-monsoon (Oct-Nov), Winter (Dec-Feb), Pre-monsoon (Mar-May)
        def get_season(m):
            if m in [6, 7, 8, 9]: return "Monsoon"
            elif m in [10, 11]: return "Post-Monsoon"
            elif m in [12, 1, 2]: return "Winter"
            else: return "Pre-Monsoon"
        df["period"] = df["time"].dt.month.apply(get_season)
    else:
        df["period"] = df["time"].dt.year.astype(str)

    results = []
    for period, group in df.groupby("period"):
        if len(group) < 5:
            continue
        y_t = group["landslide"].values
        if risk_engine.has_ml_model and risk_engine.model is not None:
            try:
                X_g = group[risk_engine.feature_columns].fillna(0)
                y_p = risk_engine.model.predict(X_g)
            except Exception:
                y_p = (group.get("rain_72h", 0) > 30).astype(int).values
        else:
            y_p = (group.get("rain_72h", 0) > 30).astype(int).values

        results.append({
            "Period": period,
            "Samples": len(group),
            "Accuracy": round(accuracy_score(y_t, y_p), 3),
            "Precision": round(precision_score(y_t, y_p, zero_division=0), 3),
            "Recall": round(recall_score(y_t, y_p, zero_division=0), 3),
            "F1 Score": round(f1_score(y_t, y_p, zero_division=0), 3)
        })

    return pd.DataFrame(results)
