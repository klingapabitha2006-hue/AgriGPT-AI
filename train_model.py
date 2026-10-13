import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

# ---------------------------------------
# CROP RECOMMENDATION ML MODEL
# Shebixion AI
# ---------------------------------------

# Dataset path
dataset_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "Crop_recommendation.csv"
)

# Load dataset
df = pd.read_csv(dataset_path)

print("Dataset loaded successfully!")
print("Dataset shape:", df.shape)
print("\nColumns:")
print(df.columns.tolist())

# Input features
features = [
    "N",
    "P",
    "K",
    "temperature",
    "humidity",
    "ph",
    "rainfall"
]

# Target
target = "label"

X = df[features]
y = df[target]

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nTraining data:", X_train.shape)
print("Testing data:", X_test.shape)

# Create Random Forest model
model = RandomForestClassifier(
    n_estimators=200,
    random_state=42
)

# Train model
print("\nTraining Random Forest model...")
model.fit(X_train, y_train)

# Prediction
y_pred = model.predict(X_test)

# Accuracy
accuracy = accuracy_score(y_test, y_pred)

print("\n---------------------------------------")
print("MODEL TRAINING COMPLETED")
print("---------------------------------------")
print(f"Accuracy: {accuracy * 100:.2f}%")

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Save model
model_path = os.path.join(
    os.path.dirname(__file__),
    "crop_model.pkl"
)

joblib.dump(model, model_path)

print("\nModel saved successfully!")
print("Model path:", model_path)