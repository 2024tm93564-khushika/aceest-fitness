# app.py
from flask import Flask, jsonify, request

app = Flask(__name__)

# Core logic extracted from Aceestver-1.1.py
PROGRAMS = {
    "Fat Loss (FL)": {
        "workout": "Mon: Back Squat 5x5 + Core\nTue: EMOM 20min Assault Bike\nWed: Bench Press + 21-15-9\nThu: Deadlift + Box Jumps\nFri: Zone 2 Cardio 30min",
        "diet": "Breakfast: Egg Whites + Oats\nLunch: Grilled Chicken + Brown Rice\nDinner: Fish Curry + Millet Roti\nTarget: ~2000 kcal",
        "calorie_factor": 22
    },
    "Muscle Gain (MG)": {
        "workout": "Mon: Squat 5x5\nTue: Bench 5x5\nWed: Deadlift 4x6\nThu: Front Squat 4x8\nFri: Incline Press 4x10\nSat: Barbell Rows 4x10",
        "diet": "Breakfast: Eggs + Peanut Butter Oats\nLunch: Chicken Biryani\nDinner: Mutton Curry + Rice\nTarget: ~3200 kcal",
        "calorie_factor": 35
    },
    "Beginner (BG)": {
        "workout": "Full Body Circuit:\n- Air Squats\n- Ring Rows\n- Push-ups\nFocus: Technique & Consistency",
        "diet": "Balanced Tamil Meals\nIdli / Dosa / Rice + Dal\nProtein Target: 120g/day",
        "calorie_factor": 26
    }
}

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "version": "1.0", "message": "ACEest Fitness API is running"}), 200

@app.route('/api/programs', methods=['GET'])
def get_programs():
    return jsonify({"programs": list(PROGRAMS.keys())}), 200

@app.route('/api/program/<string:program_id>', methods=['GET'])
def get_program_details(program_id):
    program = PROGRAMS.get(program_id)
    if program:
        return jsonify(program), 200
    return jsonify({"error": "Program not found"}), 404

@app.route('/api/calculate_calories', methods=['POST'])
def calculate_calories():
    data = request.get_json()
    if not data or 'weight' not in data or 'program' not in data:
        return jsonify({"error": "Missing weight or program data"}), 400
    
    weight = data['weight']
    program_id = data['program']
    
    program = PROGRAMS.get(program_id)
    if not program:
        return jsonify({"error": "Program not found"}), 404
        
    calories = int(weight * program["calorie_factor"])
    return jsonify({"weight": weight, "program": program_id, "estimated_calories": calories}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)