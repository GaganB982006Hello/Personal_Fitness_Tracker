from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import pandas as pd
from model import CaloriePredictor
from data_processor import FitnessDataProcessor
import os
from functools import wraps
from db_manager import DBManager

app = Flask(__name__)
app.secret_key = 'super-secret-key-for-fitness-tracker'

# Initialize model, processor and database
predictor = CaloriePredictor()
processor = FitnessDataProcessor()
db = DBManager()

# Train model if not exists
if not os.path.exists(predictor.model_path):
    print("Training model for the first time...")
    predictor.train()
else:
    predictor.load_model()

# Authentication Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session['role'] != 'admin':
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        user = db.verify_user(data['username'], data['password'])
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('index'))
        return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.form
        if db.create_user(data['username'], data['password']):
            return redirect(url_for('login', success="Account created successfully!"))
        return render_template('login.html', error="Username already exists", signup=True)
    return render_template('login.html', signup=True)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html', username=session.get('username'), role=session.get('role'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    users = db.get_all_users()
    return render_template('admin.html', users=users)

@app.route('/api/stats', methods=['GET'])
@login_required
def get_stats():
    """Returns basic statistics for the dashboard."""
    df = processor.load_and_merge()
    df_processed = processor.preprocess(df.copy())
    
    stats = {
        'total_records': len(df),
        'avg_calories': float(df['Calories'].mean()),
        'avg_heart_rate': float(df['Heart_Rate'].mean()),
        'avg_duration': float(df['Duration'].mean()),
        'gender_dist': df['Gender'].value_counts().to_dict(),
        'age_dist': {
            'Young (20-40)': int(len(df[df['Age'] < 40])),
            'Middle-Aged (40-60)': int(len(df[(df['Age'] >= 40) & (df['Age'] < 60)])),
            'Senior (60+)': int(len(df[df['Age'] >= 60]))
        },
        'bmi_dist': {
            'Underweight (<18.5)': int(len(df_processed[df_processed['BMI'] < 18.5])),
            'Normal (18.5-25)': int(len(df_processed[(df_processed['BMI'] >= 18.5) & (df_processed['BMI'] < 25)])),
            'Overweight (25-30)': int(len(df_processed[(df_processed['BMI'] >= 25) & (df_processed['BMI'] < 30)])),
            'Obese (>30)': int(len(df_processed[df_processed['BMI'] >= 30]))
        }
    }
    return jsonify(stats)

@app.route('/api/historical-data', methods=['GET'])
@login_required
def get_historical_data():
    """Returns synthetic historical data for trends."""
    days = int(request.args.get('days', 7))
    data = processor.generate_synthetic_historical(days)
    return jsonify(data)

@app.route('/api/predict', methods=['POST'])
@login_required
def predict():
    """Predicts calories based on user input."""
    try:
        data = request.json
        # Map frontend names to model names if necessary
        # Form sequence: Gender, Age, Height, Weight, Duration, Heart_Rate, Body_Temp
        input_features = {
            'Gender': 1 if data['gender'] == 'female' else 0,
            'Age': float(data['age']),
            'Height': float(data['height']),
            'Weight': float(data['weight']),
            'Duration': float(data['duration']),
            'Heart_Rate': float(data['heart_rate']),
            'Body_Temp': float(data['body_temp'])
        }
        
        prediction = predictor.predict(input_features)
        return jsonify({'calories': round(float(prediction), 2)})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
