from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import json
import google.generativeai as genai
import asyncio

app = Flask(__name__)
app.config['SECRET_KEY'] = 'swasthsathi'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

HEALTH_PLANS = {
    'basic': [
        {
            'name': 'Basic Care',
            'monthly_premium': 1000,
            'coverage': 500000,
            'features': ['Hospitalization', 'Basic Medical Tests', 'Ambulance Coverage'],
            'waiting_period': '35 days',
            'suitable_for': 'Young individuals with no pre-existing conditions'
        },
        {
            'name': 'Essential Care',
            'monthly_premium': 1500,
            'coverage': 800000,
            'features': ['Consultation Cover','Hospitalization', 'Medical Tests', 'Ambulance', 'Dental Basic'],
            'waiting_period': '30 days',
            'suitable_for': 'Young professionals seeking essential coverage'
        }
    ],
    'standard': [
        {
            'name': 'Family Care',
            'monthly_premium': 2500,
            'coverage': 1500000,
            'features': ['Family Coverage Upto 5 Member', 'Maternity', 'Child Care', 'Dental'],
            'waiting_period': '90 days',
            'suitable_for': 'Families with children'
        },
        {
            'name': 'Essesntial Plus',
            'monthly_premium': 2000,
            'coverage': 1000000,
            'features': ['Comprehensive Coverage', 'Specialist Consultation', 'Preventive Care'],
            'waiting_period': '60 days',
            'suitable_for': 'Adults seeking comprehensive coverage'
        }
    ],
    'premium': [
        {
            'name': 'Premium Care',
            'monthly_premium': 5000,
            'coverage': 5000000,
            'features': ['Global Coverage', 'Executive Health Check', 'Alternative Treatments'],
            'waiting_period': '15 days',
            'suitable_for': 'High-net-worth individuals seeking premium care'
        },
        {
            'name': 'Senior Care Gold',
            'monthly_premium': 4000,
            'coverage': 3000000,
            'features': ['Senior Citizen Coverage', 'Pre-existing Diseases', 'Home Healthcare'],
            'waiting_period': '30 days',
            'suitable_for': 'Senior citizens with pre-existing conditions'
        }
    ]
}

def get_ai_health_feedback(profile_data):
    try:
        import google.generativeai as genai
        
        api_key = "AIzaSyC60SdKieCqEY0cfBdxFTKaOSyXH9Y5_mU"
        genai.configure(api_key=api_key)
        
        health_conditions = profile_data.get('health_conditions', [])
        if not health_conditions:
            health_conditions_text = "None reported"
        else:
            health_conditions_text = ', '.join(health_conditions)
            
        age = profile_data.get('age', "Not specified")
        exercise_frequency = profile_data.get('exercise_frequency', "Not specified")
        smoking_status = profile_data.get('smoking_status', "Not specified")
        alcohol_consumption = profile_data.get('alcohol_consumption', "Not specified")
        sleep_quality = profile_data.get('sleep_quality', "Not specified")
        diet_quality = profile_data.get('diet_quality', "Not specified")
        stress_level = profile_data.get('stress_level', "Not specified")
        
        prompt = f"""
        Based on the following health profile, provide personalized lifestyle advice and health recommendations:
       
        Age: {age}
        Health Conditions: {health_conditions_text}
        Exercise Frequency: {exercise_frequency}
        Smoking Status: {smoking_status}
        Alcohol Consumption: {alcohol_consumption}
        Sleep Quality: {sleep_quality}
        Diet Quality: {diet_quality}
        Stress Level: {stress_level}
       
        Provide specific, actionable advice in these areas:
        1. Exercise recommendations
        2. Dietary suggestions
        3. Lifestyle modifications
        4. Preventive health measures
        5. Stress management techniques
       
        Format the response in HTML with appropriate headings and bullet points and don't use any bold words.
        Avoid using any code block markers in the response.
        """
        
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        
        # Clean up the response by removing markdown code block markers
        feedback = response.text
        if feedback.startswith('```html'):
            feedback = feedback[7:]
        if feedback.endswith('```'):
            feedback = feedback[:-3]
        feedback = feedback.strip()
        
        return feedback
    except Exception as e:
        return f"<h3>Health Recommendations</h3><p>We're currently unable to generate personalized recommendations. Please try again later.</p><p>Error: {str(e)}</p>"

@app.route('/generate-ai-feedback/<int:profile_id>', methods=['POST'])
@login_required
def generate_ai_feedback(profile_id):
    conn = get_db_connection()
    profile = conn.execute('''SELECT * FROM health_profiles WHERE id = ? AND user_id = ?''', (profile_id, current_user.id)).fetchone()
    conn.close()
    
    if not profile:
        return {"success": False, "message": "Profile not found"}, 404
    
    profile_data = json.loads(profile['form_data'])
    
    # Direct call with no threading or async
    ai_feedback = get_ai_health_feedback(profile_data)
    
    return {"success": True, "feedback": ai_feedback}

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS users
                   (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.execute('''CREATE TABLE IF NOT EXISTS health_profiles
                   (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    form_data TEXT NOT NULL,
                    recommended_plans TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    conn.commit()
    conn.close()

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if user:
        return User(user['id'], user['username'])
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            login_user(User(user['id'], user['username']))
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not username or not password or not confirm_password:
            flash('All fields are required')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match')
            return render_template('register.html')
        
        conn = get_db_connection()
        if conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone():
            flash('Username already exists')
            conn.close()
            return render_template('register.html')
        # Only insert if username does not exist
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                    (username, generate_password_hash(password)))
        conn.commit()
        conn.close()
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/health-form', methods=['GET', 'POST'])
@login_required
def health_form():
    if request.method == 'POST':
        form_data = request.form
        processed_data = process_form_data(form_data)
        recommended_plans = get_plan_recommendations(processed_data)
        conn = get_db_connection()
        cursor = conn.execute('''INSERT INTO health_profiles (user_id, form_data, recommended_plans) VALUES (?, ?, ?)''',
                    (current_user.id, 
                     json.dumps(dict(form_data)),
                     json.dumps(recommended_plans)))
        last_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return redirect(url_for('show_recommendations', profile_id=last_id))
    return render_template('health_form.html')

@app.route('/plans')
def all_plans():
    return render_template('all_plans.html', plans=HEALTH_PLANS)

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    profiles = conn.execute('''SELECT * FROM health_profiles WHERE user_id = ? ORDER BY created_at DESC''',(current_user.id,)).fetchall()
    
    profiles_list = []
    for profile in profiles:
        profile_dict = dict(profile)
        profile_dict['form_data'] = json.loads(profile_dict['form_data'])
        profile_dict['recommended_plans'] = json.loads(profile_dict['recommended_plans'])
        profiles_list.append(profile_dict)
    
    conn.close()
    return render_template('dashboard.html', profiles=profiles_list)

@app.route('/recommendations/<int:profile_id>')
@login_required
def show_recommendations(profile_id):
    conn = get_db_connection()
    profile = conn.execute('''SELECT * FROM health_profiles WHERE id = ? AND user_id = ?''', (profile_id, current_user.id)).fetchone()
    conn.close()
    
    if not profile:
        flash('Profile not found')
        return redirect(url_for('dashboard'))
    
    recommended_plans = json.loads(profile['recommended_plans'])
    profile_data = json.loads(profile['form_data'])
    
    # Initialize AI feedback as None - we'll generate it on demand
    ai_feedback = None
    
    return render_template('recommendations.html', 
                         plans=recommended_plans,
                         profile_data=profile_data,
                         ai_feedback=ai_feedback)

@app.route('/delete-profile/<int:profile_id>', methods=['POST'])
@login_required
def delete_profile(profile_id):
    conn = get_db_connection()
    profile = conn.execute('''SELECT user_id FROM health_profiles WHERE id = ?''', (profile_id,)).fetchone()
    if profile and profile['user_id'] == current_user.id:
        conn.execute('DELETE FROM health_profiles WHERE id = ?', (profile_id,))
        conn.commit()
        flash('Assessment deleted successfully', 'success')
    else:
        flash('Profile not found or unauthorized', 'error')
    conn.close()
    return redirect(url_for('dashboard'))

def process_form_data(form_data):
    exercise_map = {
        'sedentary': 0,
        'light': 1,
        'moderate': 2,
        'active': 3
    }
    smoking_map = {
        'never': 0,
        'former': 1,
        'current': 2
    }
    alcohol_map = {
        'never': 0,
        'occasional': 1,
        'moderate': 2,
        'frequent': 3
    }
    sleep_quality_map = {
        'poor': 0,
        'fair': 1,
        'good': 2,
        'excellent': 3
    }
    diet_quality_map = {
        'poor': 0,
        'fair': 1,
        'good': 2,
        'excellent': 3
    }
    stress_level_map = {
        'low': 0,
        'moderate': 1,
        'high': 2,
        'very_high': 3
    }
    conditions = form_data.getlist('conditions[]') if hasattr(form_data, 'getlist') else form_data.get('conditions[]', '').split(',')
    conditions = [c for c in conditions if c]
    income_map = {
        'below_30k': 1,
        '30k_50k': 2,
        '50k_75k': 3,
        '75k_100k': 4,
        'above_100k': 5
    }
    processed_data = {
        'age': int(form_data.get('age', 0)),
        'gender': form_data.get('gender', ''),
        'health_conditions': conditions,
        'has_diabetes': 'diabetes' in conditions,
        'has_heart_condition': 'heart_condition' in conditions,
        'has_hypertension': 'hypertension' in conditions,
        'has_mental_health': 'mental_health' in conditions,
        'has_physical_disability': 'physical_disability' in conditions,
        'family_history': form_data.get('family_history', ''),
        'current_medications': form_data.get('current_medications', ''),
        'recent_surgeries': form_data.get('recent_surgeries', ''),
        'exercise_frequency': form_data.get('exercise_frequency', 'sedentary'),
        'exercise_score': exercise_map.get(form_data.get('exercise_frequency', 'sedentary'), 0),
        'smoking_status': form_data.get('smoking_status', 'never'),
        'smoking_score': smoking_map.get(form_data.get('smoking_status', 'never'), 0),
        'alcohol_consumption': form_data.get('alcohol_consumption', 'never'),
        'alcohol_score': alcohol_map.get(form_data.get('alcohol_consumption', 'never'), 0),
        'sleep_quality': form_data.get('sleep_quality', 'fair'),
        'sleep_score': sleep_quality_map.get(form_data.get('sleep_quality', 'fair'), 1),
        'diet_quality': form_data.get('diet_quality', 'fair'),
        'diet_score': diet_quality_map.get(form_data.get('diet_quality', 'fair'), 1),
        'stress_level': form_data.get('stress_level', 'moderate'),
        'stress_score': stress_level_map.get(form_data.get('stress_level', 'moderate'), 1),
        'bmi': float(form_data.get('bmi', 0)) if form_data.get('bmi') else 0,
        'blood_pressure': form_data.get('blood_pressure', ''),
        'occupation': form_data.get('occupation', ''),
        'income_category': form_data.get('income_category', 'below_30k'),
        'income_score': income_map.get(form_data.get('income_category', 'below_30k'), 1)
    }
    return processed_data

def get_plan_recommendations(processed_data):    
    recommendations = []
    confidence_scores = []
    age = processed_data['age']
    has_conditions = any([
        processed_data['has_diabetes'],
        processed_data['has_heart_condition'],
        processed_data['has_hypertension'],
        processed_data['has_mental_health'],
        processed_data['has_physical_disability']
    ])
    exercise_score = processed_data['exercise_score']
    smoking_score = processed_data['smoking_score']
    alcohol_score = processed_data['alcohol_score']
    stress_score = processed_data['stress_score']
    diet_score = processed_data['diet_score']
    sleep_score = processed_data['sleep_score']
    income_score = processed_data['income_score']
    
    lifestyle_score = (
        (3 - smoking_score) * 3 + 
        (3 - alcohol_score) * 2 + 
        exercise_score * 2 + 
        diet_score * 2 + 
        sleep_score + 
        (3 - stress_score)
    ) / 11.0

    if age > 60 or (has_conditions and (smoking_score > 0 or alcohol_score > 1)):
        recommendations.extend(HEALTH_PLANS['premium'])
        confidence_scores.extend([0.85, 0.75])
        recommendations.extend(HEALTH_PLANS['standard'])
        confidence_scores.extend([0.65, 0.60])
        
    elif has_conditions or (age > 45 and (smoking_score > 0 or alcohol_score > 1)):
        recommendations.extend(HEALTH_PLANS['standard'])
        confidence_scores.extend([0.85, 0.80])
        recommendations.extend(HEALTH_PLANS['premium'])
        confidence_scores.extend([0.70, 0.65])
        
    else:
        recommendations.extend(HEALTH_PLANS['basic'])
        confidence_scores.extend([0.85, 0.80])
        if income_score >= 3:
            recommendations.extend(HEALTH_PLANS['standard'])
            confidence_scores.extend([0.75, 0.70])

    for i in range(len(confidence_scores)):
        if lifestyle_score > 2:  
            confidence_scores[i] = min(0.95, confidence_scores[i] + 0.05)
        elif lifestyle_score < 1:  
            confidence_scores[i] = max(0.50, confidence_scores[i] - 0.10)
    
    for i, plan in enumerate(recommendations):
        plan = plan.copy()
        plan['confidence_score'] = confidence_scores[i]
        recommendations[i] = plan
    
    recommendations.sort(key=lambda x: x['confidence_score'], reverse=True)
    
    return recommendations[:4]

@app.context_processor
def utility_processor():
    def format_currency(amount):
        return f"₹{amount:,.2f}"
    return dict(format_currency=format_currency)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)