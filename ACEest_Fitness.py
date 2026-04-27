# ACEest_Fitness.py (Version 3.2.4)
from flask import Flask, jsonify, request, send_file
import sqlite3
from datetime import datetime, timedelta
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
    
    # Users table
    cur.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, role TEXT)''')
    cur.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('admin','admin','Admin')")
    
    # Schema Migration for v3.2.4 (Adding Membership Columns)
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='clients'")
    if cur.fetchone():
        cur.execute("PRAGMA table_info(clients)")
        cols = {row[1] for row in cur.fetchall()}
        if "membership_status" not in cols:
            cur.execute("ALTER TABLE clients ADD COLUMN membership_status TEXT DEFAULT 'Active'")
            cur.execute("ALTER TABLE clients ADD COLUMN membership_end TEXT")
    else:
        cur.execute('''CREATE TABLE clients (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, age INTEGER, height REAL, weight REAL, program TEXT, calories INTEGER, target_weight REAL, target_adherence INTEGER, membership_status TEXT DEFAULT 'Active', membership_end TEXT)''')

    cur.execute('''CREATE TABLE IF NOT EXISTS progress (id INTEGER PRIMARY KEY AUTOINCREMENT, client_name TEXT, week TEXT, adherence INTEGER)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS workouts (id INTEGER PRIMARY KEY AUTOINCREMENT, client_name TEXT, date TEXT, workout_type TEXT, duration_min INTEGER, notes TEXT)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS metrics (id INTEGER PRIMARY KEY AUTOINCREMENT, client_name TEXT, date TEXT, weight REAL, waist REAL, bodyfat REAL)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "version": "3.2.4", "message": "ACEest API v3.2.4 (Final: Membership Edition) is running"}), 200

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT role FROM users WHERE username=? AND password=?", (data.get('username'), data.get('password')))
    row = cur.fetchone()
    conn.close()
    if row: return jsonify({"message": "Login successful", "role": row[0]}), 200
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/api/clients', methods=['POST'])
def add_client():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({"error": "Missing client data"}), 400
    program_data = PROGRAMS.get(data.get('program', 'Beginner (BG)'))
    calories = int(data.get('weight', 0) * program_data['calorie_factor']) if program_data else 0
    
    # Default 30-day membership for new clients
    mem_end = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    
    try:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("INSERT OR REPLACE INTO clients (name, age, height, weight, program, calories, target_weight, target_adherence, membership_status, membership_end) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                    (data['name'], data.get('age', 0), data.get('height', 0.0), data.get('weight', 0.0), data.get('program', 'Beginner (BG)'), calories, data.get('target_weight', 0.0), data.get('target_adherence', 0), data.get('membership_status', 'Active'), data.get('membership_end', mem_end)))
        conn.commit()
        conn.close()
        return jsonify({"message": f"Client {data['name']} saved!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# NEW v3.2.4 ENDPOINT: Check Membership
@app.route('/api/clients/<client_name>/membership', methods=['GET'])
def check_membership(client_name):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT membership_status, membership_end FROM clients WHERE name=?", (client_name,))
    row = cur.fetchone()
    conn.close()
    
    if not row:
        return jsonify({"error": "Client not found"}), 404
        
    return jsonify({"client": client_name, "status": row[0], "renewal_date": row[1]}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)