import pandas as pd

class FitnessDataProcessor:
    def __init__(self, calories_path='calories.csv', exercise_path='exercise.csv'):
        self.calories_path = calories_path
        self.exercise_path = exercise_path
        self.raw_data = None
        self.processed_data = None

    def load_and_merge(self):
        """Loads data from CSV files and merges them on User_ID."""
        calories = pd.read_csv(self.calories_path)
        exercise = pd.read_csv(self.exercise_path)
        self.raw_data = exercise.merge(calories, on="User_ID")
        return self.raw_data

    def preprocess(self, data=None):
        """Preprocesses the data: drops User_ID, calculates BMI, and encodes categorical variables."""
        if data is None:
            if self.raw_data is None:
                self.load_and_merge()
            data = self.raw_data.copy()
        
        # Calculate BMI: Weight (kg) / [Height (m)]^2
        if 'Height' in data.columns and 'Weight' in data.columns:
            # Height is in cm in the dataset
            data['BMI'] = data['Weight'] / ((data['Height'] / 100) ** 2)
            data['BMI'] = data['BMI'].round(2)

        # Drop User_ID as it is not predictive
        if 'User_ID' in data.columns:
            data = data.drop(columns=['User_ID'])
        
        # Binary encoding for Gender (male: 0, female: 1)
        if 'Gender' in data.columns:
            data['Gender'] = data['Gender'].map({'male': 0, 'female': 1})
            
        self.processed_data = data
        return data

    def generate_synthetic_historical(self, days=7):
        """Generates synthetic historical data for metrics missing in CSVs (Steps, Sleep, SpO2, Stress)."""
        import numpy as np
        from datetime import datetime, timedelta

        dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days)][::-1]
        
        # Consistent synthetic data generation
        data = {
            'dates': dates,
            'steps': [np.random.randint(4000, 12000) for _ in range(days)],
            'sleep_hours': [round(float(np.random.uniform(5, 9)), 1) for _ in range(days)],
            'spo2': [np.random.randint(95, 100) for _ in range(days)],
            'stress': [np.random.randint(10, 80) for _ in range(days)],
            'heart_rate': [np.random.randint(60, 110) for _ in range(days)],
            'calories': [np.random.randint(1500, 3000) for _ in range(days)]
        }
        return data

    def get_training_data(self):
        """Returns features (X) and target (y) for model training."""
        if self.processed_data is None:
            self.preprocess()
        
        # Maintain compatibility with the original model features
        original_features = ['Gender', 'Age', 'Height', 'Weight', 'Duration', 'Heart_Rate', 'Body_Temp']
        X = self.processed_data[original_features]
        y = self.processed_data['Calories']
        return X, y

if __name__ == "__main__":
    processor = FitnessDataProcessor()
    df = processor.load_and_merge()
    print(f"Data loaded. Shape: {df.shape}")
    X, y = processor.get_training_data()
    print(f"Features shape: {X.shape}, Target shape: {y.shape}")
    print("Preprocessed columns:", X.columns.tolist())
