# ACEest_Fitness.py (Version 1.1)
from flask import Flask, jsonify, request

app = Flask(__name__)

PROGRAMS = {
    "Fat Loss (FL)": {"calorie_factor": 22},
    "Muscle Gain (MG)": {"calorie_factor": 35},
    "Beginner (BG)": {"calorie_factor": 26}
}

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "version": "1.1", "message": "ACEest Fitness API v1.1 is running"}), 200

@app.route('/api/client/preview', methods=['POST'])
def preview_client():
    data = request.get_json()
    if not data or 'name' not in data or 'program' not in data:
        return jsonify({"error": "Missing client data"}), 400

    program_data = PROGRAMS.get(data['program'])
    if not program_data:
        return jsonify({"error": "Invalid Program"}), 400

    weight = data.get('weight', 0.0)
    calories = int(weight * program_data['calorie_factor']) if weight > 0 else 0

    response = {
        "message": f"Client {data['name']} preview generated successfully.",
        "adherence_target": data.get('adherence', 0),
        "estimated_calories": calories
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)