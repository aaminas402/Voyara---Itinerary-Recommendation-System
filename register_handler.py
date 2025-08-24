from flask import Flask, request, jsonify
import json
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyADF48lxNeI3U3TIg0F7vRMGR7f4kBNcr4"  # Replace with your actual API key
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

def load_users():
    try:z
        with open('users.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {"users": []}

def save_users(users_data):
    with open('users.json', 'w') as file:
        json.dump(users_data, file, indent=4)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Load existing users
    users_data = load_users()
    
    # Check if email already exists
    if any(user['email'] == data['email'] for user in users_data['users']):
        return jsonify({"error": "Email already registered"}), 400
    
    # Create new user with hashed password
    new_user = {
        "id": str(data['id']),
        "fullName": data['fullName'],
        "email": data['email'],
        "password": generate_password_hash(data['password']),  # Hash the password
        "phoneNumber": data['phoneNumber'],
        "dateRegistered": datetime.now().isoformat()
    }
    
    # Add new user to the list
    users_data['users'].append(new_user)
    
    # Save updated users list
    save_users(users_data)
    
    return jsonify({"message": "Registration successful"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Missing email or password"}), 400

    users_data = load_users()
    
    # Find user by email
    user = next((user for user in users_data['users'] if user['email'] == data['email']), None)
    
    if user and check_password_hash(user['password'], data['password']):
        return jsonify({
            "message": "Login successful",
            "user": {
                "id": user['id'],
                "fullName": user['fullName'],
                "email": user['email']
            }
        }), 200
    
    return jsonify({"error": "Invalid email or password"}), 401

@app.route('/generate_itinerary', methods=['POST'])
def generate_itinerary():
    try:
        data = request.json
        prompt = data.get('prompt')
        
        # Generate response using Gemini
        response = model.generate_content(prompt)
        
        return jsonify({
            'response': response.text
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000) 