# model.py

# Import necessary libraries
import xgboost as xgb
from sklearn.model_selection import train_test_split
import pandas as pd

# Load dataset
df = pd.read_csv('data.csv') # Change 'data.csv' with your csv file containing the dataset

# Split the dataset into features and target variable
X = df.drop('target', axis=1) # Change 'target' with the column name of your target variable
y = df['target'] # Change 'target' with the column name of your target variable

# Split the dataset into training set and test set
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize XGBoost classifier
model = xgb.XGBClassifier()

# Fit the model with training set
model.fit(X_train, y_train)

# Make predictions with test set
y_pred = model.predict(X_test)

# Save the model to a file
model.save_model('xgboost_model.json') # You can change 'xgboost_model.json' with your preferred filename

# The XGBoost model is now trained and saved to a file. You can load this file to make predictions on new data.