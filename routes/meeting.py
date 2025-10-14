from flask import Blueprint, jsonify, request
from config import db
from models import Meeting
from functools import wraps

meeting_bp = Blueprint('meeting', __name__)

# -------------------------------
# Simple Admin Authentication Check
# -------------------------------
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        admin_key = request.headers.get("X-Admin-Key")
        if admin_key != "supersecretadminkey":  # Change this to your real key system
            return jsonify({"error": "Unauthorized. Admin access only."}), 403
        return f(*args, **kwargs)
    return decorated_function


# -------------------------------
# CRUD Routes for Meeting
# -------------------------------

# ✅ READ all meetings
@meeting_bp.route('/meetings', methods=['GET'])
@admin_required
def get_meetings():
    meetings = Meeting.query.all()
    if not meetings:
        return jsonify({"message": "No meetings found"}), 404
    return jsonify([
        {
            "id": m.id,
            "title": m.title,
            "date": m.date,
            "deadline": m.deadline,
            "registration_amount": m.registration_amount,
            "poster_url": m.poster_url,
            "description": m.description
        } for m in meetings
    ]), 200


# ✅ READ one meeting
@meeting_bp.route('/meetings/<int:id>', methods=['GET'])
@admin_required
def get_meeting(id):
    meeting = Meeting.query.get(id)
    if not meeting:
        return jsonify({"message": "Meeting not found"}), 404
    return jsonify({
        "id": meeting.id,
        "title": meeting.title,
        "date": meeting.date,
        "deadline": meeting.deadline,
        "registration_amount": meeting.registration_amount,
        "poster_url": meeting.poster_url,
        "description": meeting.description
    }), 200


# ✅ CREATE new meeting
@meeting_bp.route('/meetings', methods=['POST'])
@admin_required
def create_meeting():
    data = request.json

    if not data.get("title") or not data.get("date") or not data.get("deadline"):
        return jsonify({"error": "Title, date, and deadline are required"}), 400

    meeting = Meeting(
        title=data["title"],
        date=data["date"],
        deadline=data["deadline"],
        registration_amount=data.get("registration_amount", 0.0),
        poster_url=data.get("poster_url"),
        description=data.get("description")
    )

    db.session.add(meeting)
    db.session.commit()

    return jsonify({"message": "Meeting created successfully", "id": meeting.id}), 201


# ✅ UPDATE a meeting
@meeting_bp.route('/meetings/<int:id>', methods=['PUT'])
@admin_required
def update_meeting(id):
    meeting = Meeting.query.get(id)
    if not meeting:
        return jsonify({"error": "Meeting not found"}), 404

    data = request.json

    meeting.title = data.get('title', meeting.title)
    meeting.date = data.get('date', meeting.date)
    meeting.deadline = data.get('deadline', meeting.deadline)
    meeting.registration_amount = data.get('registration_amount', meeting.registration_amount)
    meeting.poster_url = data.get('poster_url', meeting.poster_url)
    meeting.description = data.get('description', meeting.description)

    db.session.commit()

    return jsonify({"message": "Meeting updated successfully"}), 200


# ✅ DELETE a meeting
@meeting_bp.route('/meetings/<int:id>', methods=['DELETE'])
@admin_required
def delete_meeting(id):
    meeting = Meeting.query.get(id)
    if not meeting:
        return jsonify({"error": "Meeting not found"}), 404

    db.session.delete(meeting)
    db.session.commit()
    return jsonify({"message": "Meeting deleted successfully"}), 200
