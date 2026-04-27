# ACEest_Fitness.py (Version 2.1.2)
from flask import Flask, jsonify, request
import sqlite3
from datetime import datetime

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
    cur.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            age INTEGER,
            weight REAL,
            program TEXT,
            calories INTEGER
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            week TEXT,
            adherence INTEGER
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "version": "2.1.2", "message": "ACEest Fitness API v2.1.2 (Progress Tracking) is running"}), 200

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
        cur.execute("INSERT OR REPLACE INTO clients (name, age, weight, program, calories) VALUES (?, ?, ?, ?, ?)", 
                    (data['name'], data.get('age', 0), data.get('weight', 0.0), data['program'], calories))
        conn.commit()
        conn.close()
        return jsonify({"message": f"Client {data['name']} saved to database!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# NEW v2.1.2 ENDPOINT: Save Weekly Progress
@app.route('/api/progress', methods=['POST'])
def add_progress():
    data = request.get_json()
    if not data or 'client_name' not in data or 'adherence' not in data:
        return jsonify({"error": "Missing progress data"}), 400
    
    week = datetime.now().strftime("Week %U - %Y")
    try:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("INSERT INTO progress (client_name, week, adherence) VALUES (?, ?, ?)", 
                    (data['client_name'], week, data['adherence']))
        conn.commit()
        conn.close()
        return jsonify({"message": f"Weekly progress logged for {data['client_name']}"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# NEW v2.1.2 ENDPOINT: Get Weekly Progress
@app.route('/api/progress/<client_name>', methods=['GET'])
def get_progress(client_name):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT week, adherence FROM progress WHERE client_name=?", (client_name,))
    rows = cur.fetchall()
    conn.close()
    
    progress_list = [{"week": r[0], "adherence": r[1]} for r in rows]
    return jsonify({"client": client_name, "progress": progress_list}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)