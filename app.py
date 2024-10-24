from flask import Flask, request, jsonify
import json
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will allow CORS for all routes

# File to store the data
DATA_FILE = 'data.json'

# Initialize data store if not present
def initialize_data():
    if not os.path.exists(DATA_FILE):
        default_data = {
            "fajrAthan": "05:00",
            "fajrIqamah": "05:30",
            "zuhrAthan": "13:00",
            "zuhrIqamah": "13:30",
            "asrAthan": "16:00",
            "asrIqamah": "16:30",
            "maghribAthan": "18:15",
            "maghribIqamah": "18:30",
            "ishaAthan": "20:00",
            "ishaIqamah": "20:30",
            "jumuahAthan": "13:39",
            "jumuahIqamah": "14:00",
            "quranVerse": "Indeed, prayer prohibits immorality and wrongdoing. (29:45)",
            "announcements": "Community dinner after Maghrib",
            "donationMessage": "Kindly support your mosque with donations. test",
            "phoneMessage": "Please make sure your phones are set on silence."
        }
        with open(DATA_FILE, 'w') as file:
            json.dump(default_data, file)

# Load data from the JSON file
def load_data():
    with open(DATA_FILE, 'r') as file:
        return json.load(file)

# Save data to the JSON file
def save_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file)

# Initialize the data store on startup
initialize_data()

# Endpoint to get the current data
@app.route('/data', methods=['GET'])
def get_data():
    data = load_data()
    return jsonify(data)

# Endpoint to update the data
@app.route('/update', methods=['POST'])
def update_data():
    data = load_data()
    new_data = request.json
    app.logger.info(f"Received data for update: {new_data}")  # Logging received data
    data.update(new_data)  # Update the existing data with the new data
    save_data(data)
    app.logger.info(f"Updated data: {data}")  # Logging updated data
    return jsonify({"message": "Data updated successfully", "data": data})

# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)
