from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
import numpy as np
import joblib
import os

class HealthInsuranceRecommender:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.model_path = 'models/insurance_model.joblib'
        self.is_trained = False
        
    def generate_synthetic_data(self, n_samples=1000):
        np.random.seed(42)
        
        age = np.random.randint(18, 85, n_samples)
        exercise_score = np.random.randint(0, 4, n_samples)
        smoking_score = np.random.randint(0, 3, n_samples)
        income_score = np.random.randint(1, 6, n_samples)
        has_conditions = np.random.choice([0, 1], n_samples)
        
        X = np.column_stack([age, exercise_score, smoking_score, income_score, has_conditions])
        
        y = []
        for i in range(n_samples):
            if age[i] > 60 or (has_conditions[i] and smoking_score[i] > 0):
                y.append('premium')
            elif has_conditions[i] or (age[i] > 45 and smoking_score[i] > 0):
                y.append('standard')
            else:
                y.append('basic')
        
        return X, np.array(y)
    
    def train(self, X=None, y=None):
        if X is None or y is None:
            X, y = self.generate_synthetic_data()
        
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        joblib.dump((self.model, self.scaler), self.model_path)
    
    def load_model(self):
        if os.path.exists(self.model_path):
            self.model, self.scaler = joblib.load(self.model_path)
            self.is_trained = True
            return True
        return False
    
    def predict(self, features):
        if not self.is_trained and not self.load_model():
            self.train()
        
        features_scaled = self.scaler.transform(features)
        prediction = self.model.predict(features_scaled)
        probabilities = self.model.predict_proba(features_scaled)
        
        return prediction[0], probabilities[0]

def extract_features(form_data):
    """Extract and process features from form data"""
    conditions = form_data.getlist('conditions[]') if hasattr(form_data, 'getlist') else form_data.get('conditions[]', '').split(',')
    has_conditions = 1 if any(condition in conditions for condition in ['diabetes', 'heart_condition', 'hypertension', 'mental_health', 'physical_disability']) else 0
    exercise_map = {'sedentary': 0, 'light': 1, 'moderate': 2, 'active': 3}
    smoking_map = {'never': 0, 'former': 1, 'current': 2}
    income_map = {'below_30k': 1, '30k_50k': 2, '50k_75k': 3, '75k_100k': 4, 'above_100k': 5}
    features = np.array([[
        int(form_data.get('age', 0)),
        exercise_map.get(form_data.get('exercise_frequency', 'sedentary'), 0),
        smoking_map.get(form_data.get('smoking_status', 'never'), 0),
        income_map.get(form_data.get('income_category', 'below_30k'), 1),
        has_conditions
    ]])
    
    return features