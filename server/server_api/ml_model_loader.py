import joblib
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load models once
forecast_models = {
    "co2": joblib.load(os.path.join(BASE_DIR, "models", "forecast_co2.pkl")),
    "temp": joblib.load(os.path.join(BASE_DIR, "models", "forecast_temp.pkl")),
    "power": joblib.load(os.path.join(BASE_DIR, "models", "forecast_total_act_power.pkl")),
    "entries": joblib.load(os.path.join(BASE_DIR, "models", "forecast_total_entries.pkl")),
    "exits": joblib.load(os.path.join(BASE_DIR, "models", "forecast_total_exits.pkl")),
}

recommendation_model = joblib.load(os.path.join(BASE_DIR, "models", "recommendation_model.pkl"))
label_encoder = joblib.load(os.path.join(BASE_DIR, "models", "label_encoder.pkl"))
