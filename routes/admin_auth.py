from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
import json 
import os


admin_auth_bp = Blueprint('admin_auth', __name__)
SECRET_KEY = "your_secret_key"  # Replace with your actual secret key


# -------------- Helper function to load admin credentials from a JSON file --------------
def load_admin():
    """Load admin credentials from file"""
    try:
        with open('admin.json', 'r') as f:
            return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None 

def save_admin(admin_data):
    """Save admin credentials to file"""
    with open('admin.json', 'w')as f:
        json.dump(admin_data, f, indent=4)


# -------------- Admin Registration (only once) --------------
@admin_auth_bp.route('/register-admin', methods=['POST'])
def register_admin():
    """Register the first admin (for setup)"""
    data = request.json
    if not data.get('username') or not data.get('password'):
        return jsonify({"error": "Username and password are required"}), 400

    if os.path.exists('admin.json'):
        return jsonify({"error": "Admin already exists"}), 403


    hashed_password = generate_password_hash(data['password'])
    admin_data = {"username": data['username'], "password": hashed_password}
    save_admin(admin_data)

    return jsonify({"message": "Admin registered successfully"}), 201


# -------------- Admin Login --------------
@admin_auth_bp.route('/login', methods=['POST'])
def admin_login():
    """Admin login and get JWT token"""
    data = request.json
    if not data.get('username') or not data.get('password'):
        return jsonify({"error": "Username and password are required"}), 400

    admin = load_admin()
    if not admin or admin['username'] != data['username']:
        return jsonify({"error": "Invalid username or password"}), 401

    if not check_password_hash(admin['password'], data['password']):
        return jsonify({"error": "Invalid username or password"}), 401


    # Generate JWT token
    token = jwt.encode(
        {"username": admin['username'], "exp": datetime.utcnow() + datetime.timedelta(hours=3)},
        SECRET_KEY,
        algorithm="HS256"
    )

    return jsonify({"message": "Login successful", "token": token})


# -------------- Token Verification Decorator --------------
def token_required(f):
    """Decorator to protect admin routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[-1]

        if not token:
            return jsonify({"error": "Token is missing!"}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            admin = load_admin()
            if not admin or admin['username'] != data['username']:
                return jsonmify({"error": "Invalid token!"}), 401

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired!"}), 401
        
        expect jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token!"}), 401 
        
        return f(*args, **kwargs)
    return decorated