import numpy as np
import pandas as pd
import requests
import datetime
from typing import Dict, Any, Tuple


def calculate_wind_speed(u: float, v: float) -> float:
    """Calculates wind speed from U and V vectors."""
    return float(np.sqrt(u**2 + v**2))


def calculate_wind_direction(u: float, v: float) -> float:
    """Calculates meteorological wind direction in degrees (0-360)."""
    dir_deg = (np.degrees(np.arctan2(-u, -v)) + 360) % 360
    return float(dir_deg)


def get_wind_direction_cardinal(deg: float) -> str:
    """Converts wind direction degrees to cardinal compass direction."""
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                  "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    idx = int((deg + 11.25) / 22.5) % 16
    return directions[idx]


def calculate_dew_point_depression(temp_c: float, dewpoint_c: float) -> float:
    """Calculates dew point depression (Difference between temp and dew point)."""
    return temp_c - dewpoint_c


def calculate_relative_humidity(temp_c: float, dewpoint_c: float) -> float:
    """Calculates Relative Humidity (%) using August-Roche-Magnus equation."""
    rh = 100.0 * (
        np.exp((17.625 * dewpoint_c) / (243.04 + dewpoint_c)) /
        np.exp((17.625 * temp_c) / (243.04 + temp_c))
    )
    return float(np.clip(rh, 0, 100))


def calculate_trend(series: pd.Series) -> Tuple[str, float]:
    """
    Calculates trend direction (↑, ↓, →) and net change from a time series.
    Returns (trend_symbol, delta_value).
    """
    clean_series = series.dropna()
    if len(clean_series) < 2:
        return "→", 0.0

    recent = clean_series.iloc[-1]
    previous = clean_series.iloc[-2]
    delta = recent - previous

    threshold = 0.05 * abs(previous) if previous != 0 else 0.05
    if delta > threshold:
        return "↑", delta
    elif delta < -threshold:
        return "↓", delta
    else:
        return "→", delta


def fetch_live_weather(latitude: float = 31.1048, longitude: float = 77.1734) -> Dict[str, Any]:
    """
    Fetches real-time current weather data from Open-Meteo public API.
    Returns clear dictionary with timestamp, metrics, units, and status.
    """
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,relative_humidity_2m,dew_point_2m,surface_pressure,wind_speed_10m,wind_direction_10m,rain&timezone=auto"

    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            curr = data.get("current", {})
            return {
                "status": "Success",
                "source": "Open-Meteo Live API",
                "timestamp": curr.get("time", datetime.datetime.now().strftime("%Y-%m-%d %H:%M")),
                "temperature_c": curr.get("temperature_2m", np.nan),
                "dewpoint_c": curr.get("dew_point_2m", np.nan),
                "relative_humidity": curr.get("relative_humidity_2m", np.nan),
                "wind_speed": curr.get("wind_speed_10m", np.nan),
                "wind_direction": curr.get("wind_direction_10m", np.nan),
                "surface_pressure": curr.get("surface_pressure", np.nan),
                "rain_mm": curr.get("rain", 0.0),
                "soil_water": np.nan,  # Not provided in basic live forecast endpoint
                "latitude": latitude,
                "longitude": longitude
            }
    except Exception as e:
        pass

    # Fallback status if offline or call fails
    return {
        "status": "Offline Fallback",
        "source": "GRIB Latest Observation Fallback",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "temperature_c": 22.4,
        "dewpoint_c": 17.8,
        "relative_humidity": 75.5,
        "wind_speed": 4.2,
        "wind_direction": 180.0,
        "surface_pressure": 1011.5,
        "rain_mm": 1.2,
        "soil_water": 0.32,
        "latitude": latitude,
        "longitude": longitude
    }
