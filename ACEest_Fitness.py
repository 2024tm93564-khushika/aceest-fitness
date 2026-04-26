# ACEest_Fitness.py (Version 1.1.2)
from flask import Flask, jsonify, request
import csv
import os

app = Flask(__name__)

# In-memory storage (matching v1.1.2 logic before DB introduction)
clients = []

PROGRAMS = {
    "Fat Loss (FL)": {"calorie_factor": 22},
    "Muscle Gain (MG)": {"calorie_factor": 35},
    "Beginner (BG)": {"calorie_factor": 26}
}

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "version": "1.1.2", "message": "ACEest Fitness API v1.1.2 is running"}), 200

@app.route('/api/clients', methods=['POST'])
def add_client():
    data = request.get_json()
    if not data or 'name' not in data or 'program' not in data:
        return jsonify({"error": "Missing client data"}), 400
    
    program_data = PROGRAMS.get(data['program'])
    calories = int(data.get('weight', 0) * program_data['calorie_factor']) if program_data else 0

    client = {
        "name": data['name'],
        "age": data.get('age', 0),
        "weight": data.get('weight', 0.0),
        "program": data['program'],
        "adherence": data.get('adherence', 0),
        "calories": calories,
        "notes": data.get('notes', '')
    }
    clients.append(client)
    return jsonify({"message": f"Client {data['name']} saved successfully!", "client": client}), 201

@app.route('/api/clients', methods=['GET'])
def get_clients():
    return jsonify({"clients": clients}), 200

@app.route('/api/export', methods=['GET'])
def export_csv():
    filename = "clients_export.csv"
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Age", "Weight", "Program", "Adherence", "Notes"])
        for c in clients:
            writer.writerow([c['name'], c['age'], c['weight'], c['program'], c['adherence'], c['notes']])
    return jsonify({"message": f"Exported {len(clients)} clients to CSV"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)