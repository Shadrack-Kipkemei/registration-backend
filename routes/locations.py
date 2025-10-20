from flask import Blueprint, jsonify, request
from config import db
from models import Station, District, Church
from flask_jwt_extended import jwt_required, get_jwt_identity 


locations_bp = Blueprint('locations', __name__)


# -------------------------------
# CRUD ROUTES FOR STATIONS
# -------------------------------

# ✅ READ all stations
@locations_bp.route('/stations', methods=['GET'])
@jwt_required()
def get_stations():
    stations = Station.query.all()
    return jsonify([{"id": s.id, "name": s.name} for s in stations]), 200


# ✅ CREATE new station
@locations_bp.route('/stations', methods=['POST'])
@jwt_required()
def add_station():
    data = request.get_json()
    if not data.get('name'):
        return jsonify({"error": "Station name is required"}), 400

        new_station = Station(name=data['name'])
        db.session.add(new_station)
        db.session.commit()
        return jsonify({"message": "Station added successfully", "id": new_station.id}), 201


# ✅ UPDATE station
@locations_bp.route('/stations/<int:id>', methods=['PUT'])
@jwt_required()
def update_station(id):
    station = Station.query.get(id)
    if not station:
        return jsonify({"error": "Station not found"}), 404

        data = request.get_json()
        station.name = data.get('name', station.name)
        db.session.commit()
        return jsonify({"message": "Station updated successfully"}), 200


# ✅ DELETE station
@locations_bp.route('/stations/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_station(id):
    station = Station.query.get(id)
    if not station:
        return jsonify({"error": "Station not found"}), 404

        db.session.delete(station)
        db.session.commit()
        return jsonify({"message": "Station deleted successfully"}), 200


# -------------------------------
# CRUD ROUTES FOR DISTRICTS
# -------------------------------

# ✅ CREATE ne district
@locations_bp.route('/stations/<int:station_id>/districts', methods=['POST'])
@jwt_required()
def add_district(station_id):
    data = request.get_json()
    if not data.get('name'):
        return jsonify({"error": "District name is required"}), 400

        new_district = District(name=data['name'], station_id=station_id)
        db.session.add(new_district)
        db.session.commit()
        return jsonify({"message": "District added successfully", "id": new_district.id}), 201


# ✅ READ all districts in a station
@locations_bp.route('/stations/<int;station_id>/districts', methods=['GET'])
@jwt_required()
def get_districts(station_id):
    districts = District.query.filter_by(station_id=station_id).all()
    return jsonify([{"id": d.id, "name": d.name} for d in districts]), 200


# ✅ UPDATE district
@locations_bp.route('/districts/<int:id>', methods=['PUT'])
@jwt_required()
def update_district(id):
    district = District.query.get(id)
    if not district:
        return jsonify({"error": "District not found"}), 404

        data = request.get_json()
        district.name = data.get('name', district.name)
        db.session.commit()
        return jsonify({"message": "District updated successfully"}), 200


# ✅ DELETE district
@locations_bp.route('/districts/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_district(id):
    district = District.query.get(id)
    if not district:
        return jsonify({"error": "District not found"}), 404

        db.session.delete(district)
        db.session.commit()
        return jsonify({"message": "District deleted successfully"}), 200


# -------------------------------
# CRUD ROUTES FOR CHURCHES
# -------------------------------

# ✅ CREATE new church
@locations_bp.route('/districts/<int:district_id>/churches', methods=['POST'])
@jwt_required()
def add_church(district_id):
    data = request.get_json()
    if not data.get('name'):
        return jsonify({"error": "Church name is required"}), 400

        new_church = Church(name=data['name'], district_id=district_id)
        db.session.add(new_church)
        db.session.commit()
        return jsonify({"message": "Church added successfully", "id": new_church.id}), 201


# ✅ READ all churches in a district
@locations_bp.route('/districts/<int:district_id>/churches', methods=['GET'])
@jwt_required()
def get_churches(district_id):
    churches = Church.query.filter_by(district_id=district_id).all()
    return jsonify([{"id": c.id, "name": c.name} for c in churches]), 200


# ✅ UPDATE church
@locations_bp.route('/churches/<int:id>', methods=['PUT'])
@jwt_required()
def update_church(id):
    church = Church.query.get(id)
    if not church:
        return jsonify({"error": "Church not found"}), 404

        data = request.get_json()
        church.name = data.get('name', church.name)
        db.session.commit()
        return jsonify({"message": "Church updated successfully"}), 200


# ✅ DELETE church
@locations_bp.route('/churches/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_church(id):
    church = Church.query.get(id)
    if not church:
        return jsonify({"error": "Church not found"}), 404

        db.session.delete(church)
        db.session.commit()
        return jsonify({"message": "Church deleted successfully"}), 200