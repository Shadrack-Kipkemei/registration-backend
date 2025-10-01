from flask import Blueprint, jsonify, request 
from datetime import datetime 
import json 
import os 


meeting_bp = Blueprint('meeting', __name__)

# Load meeting config from file
def load_meeting_config():
    try:
        with open('meeting_config.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "id": 1,
            "title": "Camporee 2025",
            "date": "2025-12-01",
            "deadline": "2025-10-30",
            "registration_amount": 1000,
            "poster_url": "/default-poster.jpg",
            "description": "Join us for Spritual growth and fellowship"
        }

# Save meeting config to file
def save_meeting_config(config):
    with open('meeting_config.json', 'w') as f:
        json.dump(config, f)

@meeting_bp.route('/meeting', methods=['GET'])
def get_meeting_config():
    """Get meeting configuration"""
    meeting_config = load_meeting_config()
    return jsonify(meeting_config)

@meeting_bp.route('/meeting', methods=['PUT'])
def update_meeting_config():
    """Update meeting configuration (admin only)"""
    # In production, add authentication here
    data = request.json 

    # Validate required fields
    if not all(key in data for key in ['title', 'date', 'deadline', 'registration_amount']):
        return jsonify({"error": "Missing required fields"}), 400

        meeting_config = load_meeting_config()
        meeting_config.update(data)
        save_meeting_config(meeting_config)

        return jsonify({"message": "Meeting config updated successfully", "config": meeting_config})