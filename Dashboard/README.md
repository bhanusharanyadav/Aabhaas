# 🌧️ Aabhaas — Hybrid AI Landslide Prediction Alert Dashboard

Aabhaas is a professional, production-style weather intelligence and hybrid AI landslide prediction dashboard built with Streamlit, Plotly, Xarray, and Scikit-Learn.

## 🚀 Features

1. **Live & Historical Weather Integration**: Seamlessly combines live weather API data with ERA5 GRIB surface and pressure-level datasets.
2. **Weather Time-Series Analysis**: High-resolution interactive charts for temperature, dew point, relative humidity, wind speed & direction, surface pressure, and soil water.
3. **Atmospheric Profile Analysis**: Pressure level profiling across 1000 hPa, 850 hPa, 750 hPa, and 500 hPa to assess atmospheric instability.
4. **Dual Risk Engines**:
   - **ML-Based Landslide Probability**: Random Forest machine-learning model trained on ground-truth historical event data.
   - **Rule-Based Environmental Risk Index**: Transparent baseline environmental index derived from soil water, antecedent rainfall windows, humidity, and thermal stability.
5. **Historical Model Evaluation**: Complete ground-truth backtesting suite with Accuracy, Precision, Recall, F1 Score, ROC-AUC, Interactive Confusion Matrix, and ROC/PR curves.
6. **Interactive Spatial Risk Maps**: Modern Plotly maps (`px.scatter_map`) rendering continuous risk indices and weather variables over latitude/longitude coordinates.
7. **Alert System**: Automated threshold-based alert panel with reason, timestamp, location, and key contributing indicators.
8. **Data Source Transparency**: Full disclosure of data origins (GRIB historical, Live API, derived calculations, rule-based index, or ML prediction).

---

## 🛠️ Project Structure

```text
dashboard/
│
├── app.py                      # Main Streamlit application entry point
├── grib_loader.py              # Cached GRIB & CSV dataset loading routines
├── weather_utils.py            # Weather calculations, unit conversions, and live API fetcher
├── risk_model.py               # Risk engines (ML Classifier + Rule-based Environmental Index)
├── model_evaluation.py         # Scikit-learn backtesting evaluation suite
├── requirements.txt            # Python dependencies
├── README.md                   # System documentation
│
├── data/                       # Local GRIB storage directory
│   ├── 7e668d5a98b8be5f97255425569c428e.grib
│   ├── 12c203ba268c4538626dbbe8ea8a15cf.grib
│   └── 572a272f921c488319818645dfb980ca.grib
│
└── models/                     # Trained ML models
    └── trained_model.pkl
```

---

## 💻 Running the Dashboard

Ensure Python 3.13 and dependencies are installed:

```bash
pip install -r requirements.txt
```

Launch the Streamlit app:

```bash
streamlit run app.py
```
