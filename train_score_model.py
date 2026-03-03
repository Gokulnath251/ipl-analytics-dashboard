import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

# Load training data
data = pd.read_csv("final_score_training_data.csv")

# Features
X = data[['current_score','overs','wickets','runs_last_30','wkts_last_30']]

# Target
y = data['final_score']

# Train test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Model
model = RandomForestRegressor(
    n_estimators=200,
    random_state=42
)

# Train model
model.fit(X_train, y_train)

# Predictions
pred = model.predict(X_test)

# Evaluate
mae = mean_absolute_error(y_test, pred)

print("Model trained successfully")
print("Mean Absolute Error:", mae)

# Save model
pickle.dump(model, open("final_score_model.pkl", "wb"))

print("Model saved as final_score_model.pkl")