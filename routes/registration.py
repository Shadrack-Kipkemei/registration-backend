from flask import Blueprint, request, jsonify 
from datetime import datetime 
import json 

registration_bp = Blueprint('registration', __name__)

# Load registrations from file
def load_registrations():
    try:
        with open('registrations.json', 'r') as f:
                return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


# Save registrations to file
def save_registrations(registrations):
    with open('registrations.json', 'w') as f:
        json.dump(registrations, f)

@registration_bp.route('/register', methods=['POST'])
def register():
    """Process registration"""
    from routes.meeting import load_meeting_config

    data = request.json
    meeting_config = load_meeting_config()
    registrations = load_registrations()

    # Check if registration deadline has passed
    deadline = datetime.strptime(meeting_config['deadline'], '%Y-%m-%d')
    if datetime.now() > deadline:
        return jsonify({"error": "Registration deadline has passed"}), 400

    # Validate required fields
    required_fields = ['station', 'district', 'church', 'leaderName', 'leaderPhone', 'attendees']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    
    # Validate attendees
    if not data['attendees'] or len(data['attendees']) == 0:
        return jsonify({"error": "At least one attendee is required"}), 400

    for i, attendee in enumerate(data['attendees']):
        if not attendee.get('name') or not attendee.get('age'):
            return jsonify({"error": f"Attendee {i+1} is missing name or age"}), 400


    # Generate invoice data
    invoice_number = f"INV-{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}-{len(registrations) + 1:04d}"
    total_amount = meeting_config['registration_amount'] * len(data['attendees'])

    invoice_data = {
        "invoiceNumber": invoice_number,
        "amount": total_amount,
        "accountNumber": invoice_number,
        "date": datetime.now().strftime('%Y-%m-%d'),
        "attendees": len(data['attendees'])
    }


    # Create registration record
    registration = {
        "id": len(registrations) + 1,
        "timestamp": datetime.now().isoformat(),
        "station": data['station'],
        "district": data['district'],
        "church": data['church'],
        "leaderName": data['leaderName'],
        "leaderPhone": data['leaderPhone'],
        "attendees": data['attendees'],
        "amount": total_amount,
        "invoiceNumber": invoice_number,
        "paid": False # Will be updated when M-Pesa payment is confirmed
    }


    registrations.append(registration)
    save_registrations(registrations)


    # In production: Intergrate with M-Pesa API here
    # For now, we'll simulate a successful payment after 5 seconds
    simulate_mpesa_payment(registration['id'])

    return jsonify({
        "message": "Registration successful",
        "invoice": invoice_data,
        "registrationId": registration['id']
    })

def simulate_mpesa_payment(registration_id):
    """Simulate M-Pesa payment (for testing only)"""
    import threading
    import time 

    def update_payment():
        time.sleep(5) # Simulate payment processing time
        registrations = load_registrations()
        for reg in registrations:
            if reg['id'] == registration_id:
                reg['paid'] = True
                save_registrations(registrations)
                break

    thread = threading.Thread(target=update_payment)
    thread.start()