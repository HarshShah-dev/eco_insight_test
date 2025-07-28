import logging
from datetime import datetime, date
from typing import Dict, Any, List, Optional

import requests
from django.conf import settings
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware, get_default_timezone

from .models import WeatherLocation, WeatherHourly, WeatherDaily, WeatherCurrent

logger = logging.getLogger(__name__)

OPEN_METEO_BASE = "https://api.open-meteo.com/v1/forecast"
# Docs: /v1/forecast with hourly, daily, current, timezone, forecast_days, etc. (Open-Meteo API)
# https://open-meteo.com/en/docs
# Times can be returned in local timezone with the 'timezone' parameter.


def ensure_default_location() -> WeatherLocation:
    cfg = getattr(settings, "WEATHER_DEFAULT_LOCATION", None)
    if not cfg:
        raise RuntimeError("WEATHER_DEFAULT_LOCATION not configured in settings.py")

    obj, _ = WeatherLocation.objects.get_or_create(
        name=cfg.get("name", "Default Location"),
        defaults=dict(
            latitude=cfg["latitude"],
            longitude=cfg["longitude"],
            timezone=cfg.get("timezone", "Europe/London"),
            active=True,
        ),
    )
    # keep coordinates in sync if changed in settings
    changed = False
    for field in ("latitude", "longitude", "timezone", "active"):
        new_val = cfg.get(field, getattr(obj, field))
        if getattr(obj, field) != new_val:
            setattr(obj, field, new_val)
            changed = True
    if changed:
        obj.save(update_fields=["latitude", "longitude", "timezone", "active"])
    return obj


def _to_aware(dt_iso: str, fallback_tz=None):
    """Parse an ISO datetime string to aware datetime."""
    dt = parse_datetime(dt_iso)
    if dt is None:
        # sometimes ISO strings may come without timezone; use fallback
        dt = datetime.fromisoformat(dt_iso)
    if dt.tzinfo is None:
        tz = fallback_tz or get_default_timezone()
        dt = make_aware(dt, timezone=tz)
    return dt


def fetch_open_meteo(location: WeatherLocation) -> Dict[str, Any]:
    cfg = settings.WEATHER_DEFAULT_LOCATION
    params = {
        "latitude": location.latitude,
        "longitude": location.longitude,
        "timezone": location.timezone,
        "forecast_days": cfg.get("forecast_days", 3),
    }

    # lists → comma-separated query strings
    def list_to_param(vals: Optional[List[str]]):
        return ",".join(vals) if vals else None

    hourly = list_to_param(cfg.get("hourly"))
    daily = list_to_param(cfg.get("daily"))
    current = list_to_param(cfg.get("current"))

    if hourly:
        params["hourly"] = hourly
    if daily:
        params["daily"] = daily
    if current:
        params["current"] = current

    logger.info("Fetching Open-Meteo forecast: %s", params)
    r = requests.get(OPEN_METEO_BASE, params=params, timeout=20)
    r.raise_for_status()
    return r.json()


def upsert_weather(location: WeatherLocation, payload: Dict[str, Any]) -> None:
    tz_name = location.timezone

    # --- current ---
    current_data = payload.get("current", {})
    current_time = current_data.get("time")
    if current_time is not None:
        observed_at = _to_aware(current_time)
        curr_vals = {
            "temperature_2m": current_data.get("temperature_2m"),
            "apparent_temperature": current_data.get("apparent_temperature"),
            "precipitation": current_data.get("precipitation"),
            "weather_code": current_data.get("weather_code"),
        }
        WeatherCurrent.objects.update_or_create(
            location=location, observed_at=observed_at, defaults=curr_vals
        )

    # --- hourly ---
    hourly = payload.get("hourly", {})
    times = hourly.get("time", []) or []
    def _series(key):
        return hourly.get(key, []) or []

    fields = [
        "temperature_2m",
        "apparent_temperature",
        "precipitation",
        "precipitation_probability",
        "weather_code",
    ]
    series = {k: _series(k) for k in fields}

    # align by index
    for i, t_str in enumerate(times):
        aware_time = _to_aware(t_str)
        vals = {k: (series[k][i] if i < len(series[k]) else None) for k in fields}
        WeatherHourly.objects.update_or_create(
            location=location, time=aware_time, defaults=vals
        )

    # --- daily ---
    daily = payload.get("daily", {})
    d_times = daily.get("time", []) or []
    def _d_series(key):
        return daily.get(key, []) or []

    d_fields = [
        "temperature_2m_min",
        "temperature_2m_max",
        "precipitation_probability_max",
        "weather_code",
    ]
    d_series_map = {k: _d_series(k) for k in d_fields}

    for i, d_str in enumerate(d_times):
        d_date = date.fromisoformat(d_str.split("T")[0]) if "T" in d_str else date.fromisoformat(d_str)
        d_vals = {k: (d_series_map[k][i] if i < len(d_series_map[k]) else None) for k in d_fields}
        WeatherDaily.objects.update_or_create(
            location=location, date=d_date, defaults=d_vals
        )


def refresh_weather_for_default_location() -> WeatherLocation:
    loc = ensure_default_location()
    payload = fetch_open_meteo(loc)
    upsert_weather(loc, payload)
    return loc


# --- helper features for downstream recommendations ---

WMO_WEATHER_CODE = {
    # abbreviated map; extend as needed
    0: "Clear sky",
    1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    56: "Light freezing drizzle", 57: "Dense freezing drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    66: "Light freezing rain", 67: "Heavy freezing rain",
    71: "Slight snow fall", 73: "Moderate snow fall", 75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    85: "Slight snow showers", 86: "Heavy snow showers",
    95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail",
}


def weather_feature_snapshot(location: WeatherLocation, future_hours: int = None) -> Dict[str, Any]:
    """Summarize current + next N hours for recommender overlays."""
    from django.utils.timezone import now
    if future_hours is None:
        future_hours = getattr(settings, "WEATHER_FUTURE_HOURS_FOR_RULES", 6)

    current = WeatherCurrent.objects.filter(location=location).order_by("-observed_at").first()
    horizon = now()
    upcoming = (
        WeatherHourly.objects
        .filter(location=location, time__gte=horizon)
        .order_by("time")[:future_hours]
    )

    # aggregations
    max_precip_prob = max([h.precipitation_probability or 0 for h in upcoming], default=0)
    max_precip_amount = max([h.precipitation or 0.0 for h in upcoming], default=0.0)
    min_temp = min([h.temperature_2m for h in upcoming if h.temperature_2m is not None], default=None)
    max_temp = max([h.temperature_2m for h in upcoming if h.temperature_2m is not None], default=None)

    current_desc = WMO_WEATHER_CODE.get(int(current.weather_code), "Unknown") if current and current.weather_code is not None else None

    return {
        "current": {
            "observed_at": current.observed_at if current else None,
            "temperature_2m": current.temperature_2m if current else None,
            "apparent_temperature": current.apparent_temperature if current else None,
            "precipitation": current.precipitation if current else None,
            "weather_code": current.weather_code if current else None,
            "weather_description": current_desc,
        },
        "upcoming_hours": future_hours,
        "max_precip_probability_next_hours": max_precip_prob,
        "max_precip_amount_next_hours": max_precip_amount,
        "min_temp_next_hours": min_temp,
        "max_temp_next_hours": max_temp,
    }


def overlay_weather_rules(base_action: str, features: Dict[str, Any]) -> str:
    """
    Simple rule-layer to refine actions based on near-term weather.
    Keeps your ML output intact and adds weather-aware guidance.
    """
    parts = [base_action] if base_action else []
    max_prob = features.get("max_precip_probability_next_hours", 0) or 0
    max_precip = features.get("max_precip_amount_next_hours", 0.0) or 0.0
    min_temp = features.get("min_temp_next_hours", None)
    max_temp = features.get("max_temp_next_hours", None)

    if max_prob >= 70 or max_precip >= 1.0:
        parts.append("Rain likely soon — prefer mechanical ventilation over opening windows.")
    if max_temp is not None and max_temp >= 26:
        parts.append("Expect warmer conditions — pre-cool spaces and increase fresh air if CO₂ allows.")
    if min_temp is not None and min_temp <= 5:
        parts.append("Cold spell expected — avoid overnight purge and reduce fresh air to maintain comfort.")
    return " ".join(parts) if parts else base_action or "No recommendation."
