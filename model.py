import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os
from data_processor import FitnessDataProcessor

class CaloriePredictor:
    def __init__(self, model_path='calorie_model.joblib'):
        self.model_path = model_path
        self.model = None
        self.processor = FitnessDataProcessor()

    def train(self):
        """Trains the model using the data from CSV files."""
        print("Loading and preprocessing data...")
        X, y = self.processor.get_training_data()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)
        
        print("Training Linear Regression model...")
        self.model = LinearRegression()
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        print(f"Training complete. MSE: {mse:.2f}, R2: {r2:.4f}")
        
        # Save model
        joblib.dump(self.model, self.model_path)
        print(f"Model saved to {self.model_path}")
        return mse, r2

    def load_model(self):
        """Loads the model from disk."""
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
            return True
        return False

    def predict(self, input_data):
        """
        Predicts calories based on input features.
        input_data: list or dict containing features.
        """
        if self.model is None:
            if not self.load_model():
                raise Exception("Model not trained or loaded.")
        
        # Ensure input is a DataFrame with correct columns
        if isinstance(input_data, dict):
            input_df = pd.DataFrame([input_data])
        elif isinstance(input_data, list):
            # Assuming list matches the feature order: Gender, Age, Height, Weight, Duration, Heart_Rate, Body_Temp
            cols = ['Gender', 'Age', 'Height', 'Weight', 'Duration', 'Heart_Rate', 'Body_Temp']
            input_df = pd.DataFrame([input_data], columns=cols)
        else:
            input_df = input_data
            
        prediction = self.model.predict(input_df)
        return prediction[0]

if __name__ == "__main__":
    predictor = CaloriePredictor()
    predictor.train()
    
    # Test prediction
    # Example: female, 20, 166.0, 60.0, 14.0, 94.0, 40.3
    test_input = [1, 20, 166.0, 60.0, 14.0, 94.0, 40.3]
    pred = predictor.predict(test_input)
    print(f"Test prediction for {test_input}: {pred:.2f} calories")
