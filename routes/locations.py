from flask import Blueprint, request, jsonify
from models import db, Station, District, Church 

locations_bp = Blueprint('locations', __name__)

# STATIONS 

@locations_bp.route('/api/stations', methods=['GET'])
def get_stations():
    stations = Station.query.all()
    return jsonify([s.to_dict(rules=('-districts.churches',)) for s in stations]), 200


@locations_bp.route('/api/stations', methods=['POST'])
def add_station():
    data = request.get_json()
    name = data.get('name')

    if not name:
        return jsonify({"error": "Station name is required"}), 400

    new_station = Station(name=name)
    db.session.add(new_station)
    db.session.commit()

    return jsonify(new_station.to_dict()), 201


@locations_bp.route('/api/stations/<int:id>', methods=['PUT'])
def update_station(id):
    station = Station.query.get(id)
    if not station:
        return jsonify({"error": "Station not found"}), 404

    data = request.get_json()
    station.name = data.get('name', station.name)
    db.session.commit()

    return jsonify(station.to_dict()), 200


@locations_bp.route('/api/stations/<int:id>', methods=['DELETE'])
def delete_station(id):
    station = Station.query.get(id)
    if not station:
        return jsonify({"error": "Station not found"}), 404

    db.session.delete(station)
    db.session.commit()

    return jsonify({"message": "Station deleted"}), 200


# DISTRICTS

@locations_bp.route('/api/stations/<int:station_id>/districts', methods=['GET'])
def get_districts(station_id):
    station = Station.query.get(station_id)
    if not station:
        return jsonify({"error": "Station not found"}), 404

    return jsonify([d.to_dict(rules=('-churches',)) for d in station.districts]), 200


@locations_bp.route('/api/stations/<int:station_id>/districts', methods=['POST'])
def add_district(station_id):
    station = Station.query.get(station_id)
    if not station:
        return jsonify({"error": "Station not found"}), 404

    data = request.get_json()
    name = data.get('name')
    if not name:
        return jsonify({"error": "District name is required"}), 400

    new_district = District(name=name, station_id=station_id)
    db.session.add(new_district)
    db.session.commit()

    return jsonify(new_district.to_dict()), 201


@locations_bp.route('/api/districts/<int:id>', methods=['PUT'])
def update_district(id):
    district = District.query.get(id)
    if not district:
        return jsonify({"error": "District not found"}), 404

    data = request.get_json()
    district.name = data.get('name', district.name)
    db.session.commit()

    return jsonify(district.to_dict()), 200


@locations_bp.route('/api/districts/<int:id>', methods=['DELETE'])
def delete_district(id):
    district = District.query.get(id)
    if not district:
        return jsonify({"error": "District not found"}), 404

    db.session.delete(district)
    db.session.commit()
    return jsonify({"message": "District deleted"}), 200


# CHURCHES

@locations_bp.route('/api/stations/<int:station_id>/districts/<int:district_id>/churches', methods=['GET'])
def get_churches(station_id, district_id):
    district = District.query.filter_by(id=district_id, station_id=station_id).first()
    if not district:
        return jsonify({"error": "District not found"}), 404

    return jsonify([c.to_dict() for c in district.churches]), 200


@locations_bp.route('/api/stations/<int:station_id>/districts/<int:district_id>/churches', methods=['POST'])
def add_church(station_id, district_id):
    district = District.query.filter_by(id=district_id, station_id=station_id).first()
    if not district:
        return jsonify({"error": "District not found"}), 404

    data =  request.get_json()
    name = data.get('name')
    if not name:
        return jsonify({"error": "Church name is required"}), 400

    new_church = Church(name=name, district_id=district_id)
    db.session.add(new_church)
    db.session.commit()

    return jsonify(new_church.to_dict()), 201


@locations_bp.route('/api/churches/<int:id>', methods=['PUT'])
def update_church(id):
    church = Church.query.get(id)
    if not church:
        return jsonify({"error": "Church not found"}), 404

    data = request.get_json()
    church.name = data.get('name', church.name)
    db.session.commit()

    return jsonify(church.to_dict()), 200


@locations_bp.route('/api/churches/<int:id>', methods=['DELETE'])
def delete_church(id):
    church = Church.query.get(id)
    if not church:
        return jsonify({"error": "Church not found"}), 404

    db.session.delete(church)
    db.session.commit()
    return jsonify({"message": "Church deleted"}), 200

