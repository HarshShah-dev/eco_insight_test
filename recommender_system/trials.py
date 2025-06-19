import joblib
import pandas as pd

# Load models
forecast_co2 = joblib.load("server/server_api/models/forecast_co2.pkl")
rec_model = joblib.load("server/server_api/models/recommendation_model.pkl")
label_encoder = joblib.load("server/server_api/models/label_encoder.pkl")
# print(forecast_co2.feature_names_in_)
# Prepare input row using recent values (replace with real or test values)
# row = {
#     "co2": 950,
#     "co2_lag_1": 950,
#     "co2_lag_2": 940,
#     "co2_lag_3": 930,
#     "co2_lag_5": 910,
#     "co2_lag_10": 900,
#     "co2_lag_30": 880,
#     "co2_lag_60": 870,
#     "co2_roll_3": 940,
#     "co2_roll_5": 935,
#     "co2_roll_10": 930
# }
row = {
    "co2": 850,
    "co2_lag_1": 800,
    "co2_lag_2": 780,
    "co2_lag_3": 770,
    "co2_lag_5": 710,
    "co2_lag_10": 630,
    "co2_lag_30": 500,
    "co2_lag_60": 500,
    "co2_roll_3": 489,
    "co2_roll_5": 490,
    "co2_roll_10": 485
}
df = pd.DataFrame([row])

# Forecast CO₂ for next hour
co2_1hr = forecast_co2.predict(df)[0]
print("Forecasted CO₂ (in 1 hr):", co2_1hr)


# Features required: current + 1-hour future values
data = pd.DataFrame([{
    "co2": 500,
    "temp": 27.5,
    "total_act_power": 6500,
    "total_entries": 120,
    "total_exits": 60,
    "co2_future": co2_1hr,  # forecasted value
    "temp_future": 30.1,
    "total_act_power_future": 7100,
    "total_entries_future": 140,
    "total_exits_future": 70
}])

# Predict action
encoded = rec_model.predict(data)[0]
label = label_encoder.inverse_transform([encoded])[0]
print("Recommended Action:", label)
