import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

# === LOAD PREPROCESSED DATA ===
X_df = pd.read_csv("X_final.csv")  # contains 'sensor_type'
Y_df = pd.read_csv("Y_final.csv")

# === ONE-HOT ENCODE sensor_type ===
sensor_type_encoded = pd.get_dummies(X_df['sensor_type'], prefix='sensor')
X_df = X_df.drop(columns=['sensor_type'], errors='ignore')
X_df = pd.concat([X_df, sensor_type_encoded], axis=1)

# === CONVERT TO NUMERIC (safety) ===
X_df = X_df.apply(pd.to_numeric, errors='coerce')
Y_df = Y_df.apply(pd.to_numeric, errors='coerce')

# ✅ SAVE COLUMN ORDER BEFORE FITTING
np.save("input_columns.npy", X_df.columns.values)

# === IMPUTE + SCALE ===
imputer = SimpleImputer(strategy='mean')
scaler = StandardScaler()
X_np = scaler.fit_transform(imputer.fit_transform(X_df))
Y_np = Y_df.astype(np.float32).values

# === TRAIN/VAL SPLIT ===
X_train, X_test, Y_train, Y_test = train_test_split(X_np, Y_np, test_size=0.2, random_state=42)

X_train_tensor = torch.tensor(X_train, dtype=torch.float32)
Y_train_tensor = torch.tensor(Y_train, dtype=torch.float32)
X_test_tensor = torch.tensor(X_test, dtype=torch.float32)
Y_test_tensor = torch.tensor(Y_test, dtype=torch.float32)

# === MODEL ===
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

model = SensorRecommenderNet(input_dim=X_np.shape[1], output_dim=Y_np.shape[1])
criterion = nn.BCELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# === TRAIN LOOP ===
epochs = 25
for epoch in range(epochs):
    model.train()
    optimizer.zero_grad()
    outputs = model(X_train_tensor)
    loss = criterion(outputs, Y_train_tensor)
    loss.backward()
    optimizer.step()

    model.eval()
    with torch.no_grad():
        val_outputs = model(X_test_tensor)
        val_loss = criterion(val_outputs, Y_test_tensor)

    print(f"Epoch {epoch+1}/{epochs} - Train Loss: {loss.item():.4f}, Val Loss: {val_loss.item():.4f}")

# === SAVE ===
torch.save(model.state_dict(), "sensor_recommender_model.pt")
np.save("action_labels.npy", Y_df.columns.values)
