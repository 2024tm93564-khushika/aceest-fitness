# ACEest_Fitness.py (Version 3.1.2)
from flask import Flask, jsonify, request, send_file
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
import io
import base64
from fpdf import FPDF
import random

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
    
    # NEW in v3.1.2: Users table for Authentication
    cur.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, role TEXT)''')
    cur.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('admin','admin','Admin')")
    
    cur.execute('''CREATE TABLE IF NOT EXISTS clients (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, age INTEGER, height REAL, weight REAL, program TEXT, calories INTEGER, target_weight REAL, target_adherence INTEGER)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS progress (id INTEGER PRIMARY KEY AUTOINCREMENT, client_name TEXT, week TEXT, adherence INTEGER)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS workouts (id INTEGER PRIMARY KEY AUTOINCREMENT, client_name TEXT, date TEXT, workout_type TEXT, duration_min INTEGER, notes TEXT)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS metrics (id INTEGER PRIMARY KEY AUTOINCREMENT, client_name TEXT, date TEXT, weight REAL, waist REAL, bodyfat REAL)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "version": "3.1.2", "message": "ACEest API v3.1.2 (Auth & AI Gen) is running"}), 200

# (Standard Endpoints: Clients, Progress, Workouts, Metrics, BMI, Charts...)
@app.route('/api/clients', methods=['POST'])
def add_client():
    data = request.get_json()
    program_data = PROGRAMS.get(data.get('program', 'Beginner (BG)'))
    calories = int(data.get('weight', 0) * program_data['calorie_factor']) if program_data else 0
    try:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("INSERT OR REPLACE INTO clients (name, age, height, weight, program, calories) VALUES (?, ?, ?, ?, ?, ?)", 
                    (data['name'], data.get('age', 0), data.get('height', 0.0), data.get('weight', 0.0), data['program'], calories))
        conn.commit()
        conn.close()
        return jsonify({"message": f"Client {data['name']} saved!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ----- NEW v3.1.2 ENTERPRISE ENDPOINTS -----

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT role FROM users WHERE username=? AND password=?", (data.get('username'), data.get('password')))
    row = cur.fetchone()
    conn.close()
    
    if row:
        return jsonify({"message": "Login successful", "role": row[0]}), 200
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/api/clients/<client_name>/generate_program', methods=['POST'])
def generate_ai_program(client_name):
    data = request.get_json()
    exp_level = data.get('experience', 'beginner').lower()
    
    exercises_pool = {
        "Full Body": ["Push-Up", "Pull-Up", "Lunge", "Plank", "Dumbbell Row", "Dumbbell Press"]
    }
    
    if exp_level == "beginner":
        sets_range, reps_range, days = (2, 3), (8, 12), 3
    elif exp_level == "intermediate":
        sets_range, reps_range, days = (3, 4), (8, 15), 4
    else:
        sets_range, reps_range, days = (4, 5), (6, 15), 5

    weekly_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"][:days]
    schedule = []
    
    for day in weekly_days:
        daily_ex = random.sample(exercises_pool["Full Body"], k=3)
        for ex in daily_ex:
            schedule.append({
                "day": day,
                "exercise": ex,
                "sets": random.randint(*sets_range),
                "reps": random.randint(*reps_range)
            })
            
    return jsonify({"client": client_name, "experience": exp_level, "schedule": schedule}), 200

@app.route('/api/clients/<client_name>/report', methods=['GET'])
def generate_pdf_report(client_name):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT * FROM clients WHERE name=?", (client_name,))
    row = cur.fetchone()
    conn.close()
    
    if not row:
        return jsonify({"error": "Client not found"}), 404

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Client Report - {client_name}", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.ln(10)
    pdf.cell(0, 10, f"Name: {row[1]}", ln=True)
    pdf.cell(0, 10, f"Age: {row[2]}", ln=True)
    pdf.cell(0, 10, f"Height: {row[3]} cm", ln=True)
    pdf.cell(0, 10, f"Weight: {row[4]} kg", ln=True)
    pdf.cell(0, 10, f"Program: {row[5]}", ln=True)
    
    # Save PDF to memory buffer
    pdf_buffer = io.BytesIO(pdf.output(dest='S').encode('latin-1'))
    pdf_buffer.seek(0)
    
    return send_file(pdf_buffer, download_name=f"{client_name}_report.pdf", as_attachment=True, mimetype='application/pdf')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)