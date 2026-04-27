# ACEest_Fitness.py (Version 3.0.1)
from flask import Flask, jsonify, request
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
import io
import base64

matplotlib.use('Agg')
app = Flask(__name__)
DB_NAME = "aceest_fitness.db"

PROGRAMS = {
    "Fat Loss (FL)": {"calorie_factor": 22},
    "Muscle Gain (MG)": {"calorie_factor": 35},
    "Beginner (BG)": {"calorie_factor": 26}
}

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS clients (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, age INTEGER, height REAL, weight REAL, program TEXT, calories INTEGER, target_weight REAL, target_adherence INTEGER)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS progress (id INTEGER PRIMARY KEY AUTOINCREMENT, client_name TEXT, week TEXT, adherence INTEGER)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS workouts (id INTEGER PRIMARY KEY AUTOINCREMENT, client_name TEXT, date TEXT, workout_type TEXT, duration_min INTEGER, notes TEXT)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS metrics (id INTEGER PRIMARY KEY AUTOINCREMENT, client_name TEXT, date TEXT, weight REAL, waist REAL, bodyfat REAL)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "version": "3.0.1", "message": "ACEest API v3.0.1 (Analytics Engine) is running"}), 200

@app.route('/api/clients', methods=['POST'])
def add_client():
    data = request.get_json()
    if not data or 'name' not in data or 'program' not in data:
        return jsonify({"error": "Missing client data"}), 400
    program_data = PROGRAMS.get(data['program'])
    calories = int(data.get('weight', 0) * program_data['calorie_factor']) if program_data else 0
    try:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("INSERT OR REPLACE INTO clients (name, age, height, weight, program, calories, target_weight, target_adherence) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                    (data['name'], data.get('age', 0), data.get('height', 0.0), data.get('weight', 0.0), data['program'], calories, data.get('target_weight', 0.0), data.get('target_adherence', 0)))
        conn.commit()
        conn.close()
        return jsonify({"message": f"Client {data['name']} saved!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/progress', methods=['POST'])
def add_progress():
    data = request.get_json()
    week = datetime.now().strftime("Week %U - %Y")
    try:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("INSERT INTO progress (client_name, week, adherence) VALUES (?, ?, ?)", (data['client_name'], week, data['adherence']))
        conn.commit()
        conn.close()
        return jsonify({"message": f"Weekly progress logged"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/workouts', methods=['POST'])
def add_workout():
    data = request.get_json()
    try:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("INSERT INTO workouts (client_name, date, workout_type, duration_min, notes) VALUES (?, ?, ?, ?, ?)", 
                    (data['client_name'], data['date'], data.get('workout_type', 'Mixed'), data.get('duration_min', 60), data.get('notes', '')))
        conn.commit()
        conn.close()
        return jsonify({"message": f"Workout logged"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/metrics', methods=['POST'])
def add_metrics():
    data = request.get_json()
    try:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("INSERT INTO metrics (client_name, date, weight, waist, bodyfat) VALUES (?, ?, ?, ?, ?)", 
                    (data['client_name'], data['date'], data.get('weight', 0.0), data.get('waist', 0.0), data.get('bodyfat', 0.0)))
        conn.commit()
        conn.close()
        return jsonify({"message": f"Metrics logged"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ----- NEW v3.0.1 ANALYTICS ENDPOINTS -----

@app.route('/api/clients/<client_name>/bmi', methods=['GET'])
def get_bmi(client_name):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT height, weight FROM clients WHERE name=?", (client_name,))
    data = cur.fetchone()
    conn.close()
    
    if not data or not data[0] or not data[1]:
        return jsonify({"error": "Height and weight data missing"}), 404
        
    height_cm, weight_kg = data[0], data[1]
    if height_cm <= 0 or weight_kg <= 0:
        return jsonify({"error": "Invalid height/weight"}), 400
        
    h_m = height_cm / 100.0
    bmi = round(weight_kg / (h_m * h_m), 1)
    
    if bmi < 18.5:
        category, risk = "Underweight", "Potential nutrient deficiency, low energy."
    elif bmi < 25:
        category, risk = "Normal", "Low risk if active and strong."
    elif bmi < 30:
        category, risk = "Overweight", "Moderate risk; focus on adherence and progressive activity."
    else:
        category, risk = "Obese", "Higher risk; prioritize fat loss, consistency, and supervision."
        
    return jsonify({"client": client_name, "bmi": bmi, "category": category, "risk_note": risk}), 200

@app.route('/api/metrics/<client_name>/chart', methods=['GET'])
def get_weight_chart(client_name):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT date, weight FROM metrics WHERE client_name=? AND weight IS NOT NULL ORDER BY date", (client_name,))
    data = cur.fetchall()
    conn.close()
    if not data: return jsonify({"error": "No data"}), 404
    
    plt.figure(figsize=(8, 4))
    plt.plot([r[0] for r in data], [r[1] for r in data], marker="o", color="orange")
    plt.title(f"Weight Trend – {client_name}")
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    return jsonify({"chart_image": base64.b64encode(buf.getvalue()).decode('utf-8')}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)