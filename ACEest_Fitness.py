# ACEest_Fitness.py (Version 2.0.1)
from flask import Flask, jsonify, request
import sqlite3

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
    # Create clients table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            age INTEGER,
            weight REAL,
            program TEXT,
            calories INTEGER,
            adherence INTEGER
        )
    ''')
    # Create progress table (introduced in v2.0.1)
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

# Initialize DB on startup
init_db()

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "version": "2.0.1", "message": "ACEest Fitness API v2.0.1 (SQLite Enabled) is running"}), 200

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
        cur.execute("INSERT OR REPLACE INTO clients (name, age, weight, program, calories, adherence) VALUES (?, ?, ?, ?, ?, ?)", 
                    (data['name'], data.get('age', 0), data.get('weight', 0.0), data['program'], calories, data.get('adherence', 0)))
        conn.commit()
        conn.close()
        return jsonify({"message": f"Client {data['name']} saved to database!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/clients', methods=['GET'])
def get_clients():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT name, age, weight, program, calories, adherence FROM clients")
    rows = cur.fetchall()
    conn.close()
    
    clients_list = [{"name": r[0], "age": r[1], "weight": r[2], "program": r[3], "calories": r[4], "adherence": r[5]} for r in rows]
    return jsonify({"clients": clients_list}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)