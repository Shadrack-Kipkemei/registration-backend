from flask import Blueprint, jsonify, request
from config import db
from models import Meeting
from flask_jwt_extended import jwt_required, get_jwt_identity

meeting_bp = Blueprint('meeting', __name__)

# -------------------------------
# CRUD ROUTES FOR MEETING (ADMIN ONLY)
# -------------------------------

# ✅ READ all meetings
@meeting_bp.route('/meetings', methods=['GET'])
@jwt_required()
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
@jwt_required()
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


# ✅ CREATE a new meeting
@meeting_bp.route('/meetings', methods=['POST'])
@jwt_required()
def create_meeting():
    data = request.get_json()

    required_fields = ["title", "date", "deadline"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

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


# ✅ UPDATE meeting
@meeting_bp.route('/meetings/<int:id>', methods=['PUT'])
@jwt_required()
def update_meeting(id):
    meeting = Meeting.query.get(id)
    if not meeting:
        return jsonify({"error": "Meeting not found"}), 404

    data = request.get_json()
    meeting.title = data.get('title', meeting.title)
    meeting.date = data.get('date', meeting.date)
    meeting.deadline = data.get('deadline', meeting.deadline)
    meeting.registration_amount = data.get('registration_amount', meeting.registration_amount)
    meeting.poster_url = data.get('poster_url', meeting.poster_url)
    meeting.description = data.get('description', meeting.description)

    db.session.commit()
    return jsonify({"message": "Meeting updated successfully"}), 200


# ✅ DELETE meeting
@meeting_bp.route('/meetings/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_meeting(id):
    meeting = Meeting.query.get(id)
    if not meeting:
        return jsonify({"error": "Meeting not found"}), 404

    db.session.delete(meeting)
    db.session.commit()
    return jsonify({"message": "Meeting deleted successfully"}), 200
