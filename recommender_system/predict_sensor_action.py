import torch
import torch.nn as nn
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

# === DEFINE MODEL CLASS ===
class SensorRecommenderNet(nn.Module):
    def __init__(self, input_dim, output_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, output_dim),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.net(x)

# === LOAD METADATA ===
action_labels = np.load("action_labels.npy", allow_pickle=True)
input_columns = np.load("input_columns.npy", allow_pickle=True)

# === LOAD MODEL ===
model = SensorRecommenderNet(input_dim=len(input_columns), output_dim=len(action_labels))
model.load_state_dict(torch.load("sensor_recommender_model.pt"))
model.eval()

# === FIT IMPUTER AND SCALER ON THE SAME COLUMNS USED DURING TRAINING ===
X_train = pd.read_csv("X_final.csv")

# One-hot encode sensor_type (must match training)
sensor_type_encoded = pd.get_dummies(X_train['sensor_type'], prefix='sensor')
X_train = X_train.drop(columns=['sensor_type'], errors='ignore')
X_train = pd.concat([X_train, sensor_type_encoded], axis=1)

# Align column order
X_train = X_train[input_columns]

# Fit imputer and scaler
imputer = SimpleImputer(strategy='mean')
scaler = StandardScaler()
imputer.fit(X_train)
scaler.fit(imputer.transform(X_train))

# === PREDICTION FUNCTION ===
def predict_action(new_data_dict):
    """
    new_data_dict: sensor values and sensor_type
    Example:
        {
            "co2": 950,
            "temp": 28,
            "pm2p5": 42,
            "a_current": 12,
            "total_act_power": 8000,
            "entries": 3,
            "total_entries": 150,
            "total_exits": 20,
            "sensor_type": "AQ"
        }
    """
    df = pd.DataFrame([new_data_dict])
    
    # One-hot encode sensor_type
    sensor_type_encoded = pd.get_dummies(df['sensor_type'], prefix='sensor')
    df = df.drop(columns=['sensor_type'], errors='ignore')
    df = pd.concat([df, sensor_type_encoded], axis=1)

    # Ensure all expected columns are present
    for col in input_columns:
        if col not in df.columns:
            df[col] = np.nan  # fill missing columns

    # Align columns to training order
    df = df[input_columns]

    # Impute and scale
    X = scaler.transform(imputer.transform(df))

    # Predict
    x_tensor = torch.tensor(X, dtype=torch.float32)
    with torch.no_grad():
        output = model(x_tensor).numpy()[0]

    threshold = 0.5
    predicted_actions = [label for i, label in enumerate(action_labels) if output[i] >= threshold]
    return predicted_actions

# === TEST EXAMPLE ===
if __name__ == "__main__":
    test_input = {
        "co2": 500,
        "temp": 23,
        "pm2p5": 5,
        "a_current": 8,
        "total_act_power": 5000,
        "entries": 1,
        "total_entries": 30,
        "total_exits": 20,
        "sensor_type": "AQ"
    }

    actions = predict_action(test_input)
    print("Recommended Actions:", actions)
