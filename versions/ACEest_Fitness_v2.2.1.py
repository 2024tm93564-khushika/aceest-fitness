# ACEest_Fitness.py (Version 2.2.1)
from flask import Flask, jsonify, request
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
import io
import base64

# Force matplotlib to not use any Xwindows backend (since we are in Docker)
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
    cur.execute('''CREATE TABLE IF NOT EXISTS clients (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, age INTEGER, weight REAL, program TEXT, calories INTEGER)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS progress (id INTEGER PRIMARY KEY AUTOINCREMENT, client_name TEXT, week TEXT, adherence INTEGER)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "version": "2.2.1", "message": "ACEest Fitness API v2.2.1 (Chart Engine) is running"}), 200

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

# NEW v2.2.1 ENDPOINT: Generate Progress Chart
@app.route('/api/progress/<client_name>/chart', methods=['GET'])
def get_progress_chart(client_name):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT week, adherence FROM progress WHERE client_name=? ORDER BY id", (client_name,))
    data = cur.fetchall()
    conn.close()

    if not data:
        return jsonify({"error": "No progress data available for this client"}), 404

    weeks = [row[0] for row in data]
    adherence = [row[1] for row in data]

    # Generate the Matplotlib chart
    plt.figure(figsize=(8, 4))
    plt.plot(weeks, adherence, marker="o", linewidth=2)
    plt.title(f"Weekly Adherence Progress – {client_name}")
    plt.xlabel("Week")
    plt.ylabel("Adherence (%)")
    plt.ylim(0, 100)
    plt.grid(True)
    plt.tight_layout()

    # Save chart to memory buffer as PNG
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    # Encode as Base64 string to send over JSON
    chart_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return jsonify({"client": client_name, "chart_image": chart_base64}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)