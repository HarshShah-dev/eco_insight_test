from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

import pandas as pd

# Reload the three sensor data files
aq_path = "recommender-system\AQ_data.csv"
em_path = "recommender-system\EM_data.csv"
oc_path = "recommender-system\OC_data.csv"

aq_df = pd.read_csv(aq_path)
em_df = pd.read_csv(em_path)
oc_df = pd.read_csv(oc_path)

# Add sensor_type column to each
aq_df['sensor_type'] = 'AQ'
em_df['sensor_type'] = 'EM'
oc_df['sensor_type'] = 'OC'

# Step 1: Concatenate all data
combined_df = pd.concat([aq_df, em_df, oc_df], ignore_index=True)
print(combined_df.head(10))

# Step 2: Keep a copy of actions and sensor_type
actions = combined_df['action'].str.split(' \| ')
sensor_type = combined_df['sensor_type']

# Step 3: Drop non-feature columns
non_feature_cols = ['id', 'created_at', 'version', 'firmware_version',
                    'mac', 'frame_version', 'peripheral_support', 'digital_signature',
                    'raw_data', 'salt', 'sensor_id', 'device', 'device_id',
                    'action', 'sensor_type']
feature_df = combined_df.drop(columns=[col for col in non_feature_cols if col in combined_df.columns])

# Step 4: Convert everything to numeric where possible
feature_df = feature_df.apply(pd.to_numeric, errors='coerce')

# Step 5: Impute missing values and scale
imputer = SimpleImputer(strategy='mean')
scaler = StandardScaler()
X_imputed = imputer.fit_transform(feature_df)
X_scaled = scaler.fit_transform(X_imputed)

# Step 6: Multi-label encode the action column
mlb = MultiLabelBinarizer()
Y_encoded = mlb.fit_transform(actions)

# Package the final dataset
X_final = pd.DataFrame(X_scaled, columns=[f'feature_{i}' for i in range(X_scaled.shape[1])])
Y_final = pd.DataFrame(Y_encoded, columns=mlb.classes_)
X_final['sensor_type'] = sensor_type.values  # Retain for model use

# import ace_tools as tools; tools.display_dataframe_to_user(name="Processed Sensor Features", dataframe=X_final)
print(X_final.shape, Y_final.shape)

X_final.to_csv("X_final.csv", index=False)
Y_final.to_csv("Y_final.csv", index=False)
