# ACEest_Fitness.py (Version 2.2.4)
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
    
    # Schema Migration: Check if clients table needs updating
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='clients'")
    if cur.fetchone():
        cur.execute("PRAGMA table_info(clients)")
        cols = {row[1] for row in cur.fetchall()}
        required = {"height", "target_weight", "target_adherence"}
        if not required.issubset(cols):
            cur.execute("DROP TABLE clients") # Drop old schema to rebuild
            
    cur.execute('''CREATE TABLE IF NOT EXISTS clients (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, age INTEGER, height REAL, weight REAL, program TEXT, calories INTEGER, target_weight REAL, target_adherence INTEGER)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS progress (id INTEGER PRIMARY KEY AUTOINCREMENT, client_name TEXT, week TEXT, adherence INTEGER)''')
    
    # NEW in v2.2.4
    cur.execute('''CREATE TABLE IF NOT EXISTS workouts (id INTEGER PRIMARY KEY AUTOINCREMENT, client_name TEXT, date TEXT, workout_type TEXT, duration_min INTEGER, notes TEXT)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS metrics (id INTEGER PRIMARY KEY AUTOINCREMENT, client_name TEXT, date TEXT, weight REAL, waist REAL, bodyfat REAL)''')
    
    conn.commit()
    conn.close()

init_db()

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "version": "2.2.4", "message": "ACEest API v2.2.4 (Expanded Schema) is running"}), 200

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

@app.route('/api/progress/<client_name>/chart', methods=['GET'])
def get_progress_chart(client_name):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT week, adherence FROM progress WHERE client_name=? ORDER BY id", (client_name,))
    data = cur.fetchall()
    conn.close()
    if not data: return jsonify({"error": "No data"}), 404
    
    plt.figure(figsize=(8, 4))
    plt.plot([r[0] for r in data], [r[1] for r in data], marker="o")
    plt.title(f"Progress – {client_name}")
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    return jsonify({"chart_image": base64.b64encode(buf.getvalue()).decode('utf-8')}), 200

# NEW v2.2.4 ENDPOINT: Workouts
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
        return jsonify({"message": f"Workout logged for {data['client_name']}"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# NEW v2.2.4 ENDPOINT: Metrics
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
        return jsonify({"message": f"Metrics logged for {data['client_name']}"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)