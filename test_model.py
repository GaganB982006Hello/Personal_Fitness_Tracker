import unittest
import os
import pandas as pd
from model import CaloriePredictor

class TestCaloriePredictor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.predictor = CaloriePredictor(model_path='test_model.joblib')
        cls.predictor.train()

    def test_model_file_exists(self):
        self.assertTrue(os.path.exists('test_model.joblib'))

    def test_prediction_output_type(self):
        # female, 20, 166.0, 60.0, 14.0, 94.0, 40.3
        test_input = [1, 20, 166.0, 60.0, 14.0, 94.0, 40.3]
        prediction = self.predictor.predict(test_input)
        self.assertIsInstance(prediction, (float, int))
        self.assertGreater(prediction, 0)

    def test_prediction_with_dict(self):
        test_input = {
            'Gender': 0, # male
            'Age': 25,
            'Height': 180.0,
            'Weight': 80.0,
            'Duration': 30.0,
            'Heart_Rate': 120.0,
            'Body_Temp': 41.0
        }
        prediction = self.predictor.predict(test_input)
        self.assertIsInstance(prediction, (float, int))
        self.assertGreater(prediction, 0)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists('test_model.joblib'):
            os.remove('test_model.joblib')

if __name__ == '__main__':
    unittest.main()
