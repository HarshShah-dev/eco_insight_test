# full_pipeline.py
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, mean_squared_error
import joblib
import os
from datetime import datetime, timedelta
import random

FORECAST_TARGETS = ['co2', 'temp', 'total_act_power', 'total_entries', 'total_exits']
FREQ = '1min'
FORECAST_HORIZON = 60

# -------------------------------
# Step 1: Preprocessing & Balancing with Synthetic Data
# -------------------------------
def generate_synthetic_rows(start_time, num_samples):
    rows = []
    for i in range(num_samples):
        timestamp = (start_time + timedelta(minutes=i)).replace(tzinfo=None)
        rows.extend([
            {'timestamp': timestamp, 'co2': 1100, 'temp': 22, 'pm2p5': 20, 'total_act_power': 3000,
             'total_entries': 30, 'total_exits': 20, 'action': 'ALERT - HIGH_CO2 - Increase Ventilation'},
            {'timestamp': timestamp + timedelta(seconds=1), 'co2': 500, 'temp': 22, 'pm2p5': 40, 'total_act_power': 3000,
             'total_entries': 30, 'total_exits': 20, 'action': 'HIGH_PM2P5 - Increase Ventilation'},
            {'timestamp': timestamp + timedelta(seconds=2), 'co2': 500, 'temp': 15, 'pm2p5': 20, 'total_act_power': 3000,
             'total_entries': 30, 'total_exits': 20, 'action': 'LOW_TEMP - Increase Heating'},
            {'timestamp': timestamp + timedelta(seconds=3), 'co2': 500, 'temp': 22, 'pm2p5': 20, 'total_act_power': 7500,
             'total_entries': 30, 'total_exits': 20, 'action': 'HIGH_POWER_USAGE'},
            {'timestamp': timestamp + timedelta(seconds=4), 'co2': 500, 'temp': 22, 'pm2p5': 20, 'total_act_power': 3000,
             'total_entries': 150, 'total_exits': 20, 'action': 'VERY_POPULATED - Increase HVAC'},
             {'timestamp': timestamp + timedelta(seconds=5), 'co2': 500, 'temp': 27, 'pm2p5': 20, 'total_act_power': 3000,
             'total_entries': 30, 'total_exits': 20, 'action': 'HIGH_TEMP - Increase Cooling'},
        ])
    return pd.DataFrame(rows)

def preprocess_and_balance(aq_path, em_path, oc_path):
    aq_df = pd.read_csv(aq_path)
    em_df = pd.read_csv(em_path)
    oc_df = pd.read_csv(oc_path)

    aq_df['timestamp'] = pd.to_datetime(aq_df['timestamp']).dt.tz_localize(None).dt.floor(FREQ)
    em_df['timestamp'] = pd.to_datetime(em_df['timestamp']).dt.tz_localize(None).dt.floor(FREQ)
    oc_df['timestamp'] = pd.to_datetime(oc_df['timestamp']).dt.tz_localize(None).dt.floor(FREQ)

    aq = aq_df[['timestamp', 'co2', 'temp', 'pm2p5']].groupby('timestamp').mean().reset_index()
    em = em_df[['timestamp', 'total_act_power']].groupby('timestamp').mean().reset_index()
    oc = oc_df[['timestamp', 'total_entries', 'total_exits']].groupby('timestamp').mean().reset_index()

    df = aq.merge(em, on='timestamp', how='outer').merge(oc, on='timestamp', how='outer')
    df = df.sort_values('timestamp').ffill().dropna()
    df['action'] = 'NORMAL'

    synthetic_df = generate_synthetic_rows(datetime(2025, 1, 1), 10000)
    full_df = pd.concat([df, synthetic_df], ignore_index=True).sort_values('timestamp')
    return full_df


# -------------------------------
# Step 2: Forecasting Model (1-hour ahead)
# -------------------------------
def add_time_features(df, target):
    df = df.copy()
    for lag in [1, 2, 3, 5, 10, 30, 60]:
        df[f'{target}_lag_{lag}'] = df[target].shift(lag)
    for window in [3, 5, 10]:
        df[f'{target}_roll_{window}'] = df[target].rolling(window).mean()
    df[f'{target}_target'] = df[target].shift(-FORECAST_HORIZON)
    return df.dropna()

def train_forecast_models(df):
    models = {}
    for target in FORECAST_TARGETS:
        feat_df = add_time_features(df, target)
        X = feat_df[[col for col in feat_df.columns if col.startswith(target) and 'target' not in col]]
        y = feat_df[f'{target}_target']
        X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=False, test_size=0.2)
        model = GradientBoostingRegressor()
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        print(f"{target} (1-hour forecast) RMSE: {np.sqrt(mean_squared_error(y_test, y_pred)):.2f}")
        models[target] = model
    return models

# -------------------------------
# Step 3 & 4: Recommendation Model
# -------------------------------
def train_recommendation_model(df):
    for target in FORECAST_TARGETS:
        df[f'{target}_future'] = df[target].shift(-FORECAST_HORIZON)
    df = df.dropna()

    features = FORECAST_TARGETS + [f'{t}_future' for t in FORECAST_TARGETS]
    X = df[features]
    le = LabelEncoder()
    y = le.fit_transform(df['action'])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)

    print("\nRecommendation Model Report:\n")
    print(classification_report(y_test, y_pred, target_names=le.classes_))
    return clf, le

# -------------------------------
# Run All
# -------------------------------
def run_all(aq_path, em_path, oc_path, model_dir='models'):
    os.makedirs(model_dir, exist_ok=True)
    df = preprocess_and_balance(aq_path, em_path, oc_path)
    forecast_models = train_forecast_models(df)
    rec_model, label_encoder = train_recommendation_model(df)

    for name, model in forecast_models.items():
        joblib.dump(model, os.path.join(model_dir, f"forecast_{name}.pkl"))
    joblib.dump(rec_model, os.path.join(model_dir, "recommendation_model.pkl"))
    joblib.dump(label_encoder, os.path.join(model_dir, "label_encoder.pkl"))

    print("\nAll models saved.")

# Example usage:
run_all("recommender_system/AQ_data.csv", "recommender_system/EM_data.csv", "recommender_system/OC_data.csv")  

# run_all(r"recommender_system\AQ_data.csv", r"recommender_system\EM_data.csv", r"recommender_system\OC_data.csv")

