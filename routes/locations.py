from flask import Blueprint, request, jsonify
import json

locations_bp = Blueprint('locations', __name__)

# Load locations from file
def load_locations():
    try:
        with open('locations.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "stations": [
                {"id": 1, "name": "Eldoret East Station", "districts": []},
                {"id": 2, "name": "Eldoret North Station", "districts": []},
                {"id": 3, "name": "Eldoret West Station", "districts": []},
                {"id": 4, "name": "Eldoret South Station", "districts": []},
                {"id": 5, "name": "Segero Station", "districts": []}
            ]
        }

# Save locations to file
def save_locations(locations):
    with open('locations.json', 'w') as f:
        json.dump(locations, f, indent=4)


# ===================== GET ROUTES =====================
@locations_bp.route('/stations', methods=['GET'])
def get_stations():
    """Get all stations"""
    locations = load_locations()
    return jsonify([{"id": s["id"], "name": s["name"]} for s in locations["stations"]])


@locations_bp.route('/stations/<int:station_id>/districts', methods=['GET'])
def get_districts(station_id):
    """Get districts by station ID"""
    locations = load_locations()
    station = next((s for s in locations["stations"] if s["id"] == station_id), None)
    if not station:
        return jsonify({"error": "Station not found"}), 404

    return jsonify([{"id": d["id"], "name": d["name"]} for d in station["districts"]])


@locations_bp.route('/stations/<int:station_id>/districts/<int:district_id>/churches', methods=['GET'])
def get_churches(station_id, district_id):
    """Get churches by district ID"""
    locations = load_locations()
    station = next((s for s in locations["stations"] if s["id"] == station_id), None)
    if not station:
        return jsonify({"error": "Station not found"}), 404

    district = next((d for d in station["districts"] if d["id"] == district_id), None)
    if not district:
        return jsonify({"error": "District not found"}), 404

    return jsonify([{"id": c["id"], "name": c["name"]} for c in district["churches"]])


# ===================== CREATE ROUTES =====================
@locations_bp.route('/stations', methods=['POST'])
def add_station():
    """Add a new station (admin only)"""
    data = request.json
    locations = load_locations()

    if not data.get('name'):
        return jsonify({"error": "Station name is required"}), 400

    new_id = max([s["id"] for s in locations["stations"]], default=0) + 1
    new_station = {"id": new_id, "name": data['name'], "districts": []}
    locations["stations"].append(new_station)
    save_locations(locations)

    return jsonify({"message": "Station added successfully", "station": new_station})


@locations_bp.route('/stations/<int:station_id>/districts', methods=['POST'])
def add_district(station_id):
    """Add a new district to a station (admin only)"""
    data = request.json
    locations = load_locations()

    if not data.get('name'):
        return jsonify({"error": "District name is required"}), 400

    station = next((s for s in locations["stations"] if s["id"] == station_id), None)
    if not station:
        return jsonify({"error": "Station not found"}), 404

    new_id = max([d["id"] for d in station["districts"]], default=0) + 1
    new_district = {"id": new_id, "name": data['name'], "churches": []}
    station["districts"].append(new_district)
    save_locations(locations)

    return jsonify({"message": "District added successfully", "district": new_district})


@locations_bp.route('/stations/<int:station_id>/districts/<int:district_id>/churches', methods=['POST'])
def add_church(station_id, district_id):
    """Add a new church to a district (admin only)"""
    data = request.json
    locations = load_locations()

    if not data.get('name'):
        return jsonify({"error": "Church name is required"}), 400

    station = next((s for s in locations["stations"] if s["id"] == station_id), None)
    if not station:
        return jsonify({"error": "Station not found"}), 404

    district = next((d for d in station["districts"] if d["id"] == district_id), None)
    if not district:
        return jsonify({"error": "District not found"}), 404

    new_id = max([c["id"] for c in district["churches"]], default=0) + 1
    new_church = {"id": new_id, "name": data['name']}
    district["churches"].append(new_church)
    save_locations(locations)

    return jsonify({"message": "Church added successfully", "church": new_church})


# ===================== UPDATE ROUTES =====================
@locations_bp.route('/stations/<int:station_id>', methods=['PUT'])
def update_station(station_id):
    """Update a station name"""
    data = request.json
    locations = load_locations()

    station = next((s for s in locations["stations"] if s["id"] == station_id), None)
    if not station:
        return jsonify({"error": "Station not found"}), 404

    if not data.get('name'):
        return jsonify({"error": "New name is required"}), 400

    station["name"] = data["name"]
    save_locations(locations)
    return jsonify({"message": "Station updated successfully", "station": station})


@locations_bp.route('/stations/<int:station_id>/districts/<int:district_id>', methods=['PUT'])
def update_district(station_id, district_id):
    """Update a district name"""
    data = request.json
    locations = load_locations()

    station = next((s for s in locations["stations"] if s["id"] == station_id), None)
    if not station:
        return jsonify({"error": "Station not found"}), 404

    district = next((d for d in station["districts"] if d["id"] == district_id), None)
    if not district:
        return jsonify({"error": "District not found"}), 404

    if not data.get('name'):
        return jsonify({"error": "New name is required"}), 400

    district["name"] = data["name"]
    save_locations(locations)
    return jsonify({"message": "District updated successfully", "district": district})


@locations_bp.route('/stations/<int:station_id>/districts/<int:district_id>/churches/<int:church_id>', methods=['PUT'])
def update_church(station_id, district_id, church_id):
    """Update a church name"""
    data = request.json
    locations = load_locations()

    station = next((s for s in locations["stations"] if s["id"] == station_id), None)
    if not station:
        return jsonify({"error": "Station not found"}), 404

    district = next((d for d in station["districts"] if d["id"] == district_id), None)
    if not district:
        return jsonify({"error": "District not found"}), 404

    church = next((c for c in district["churches"] if c["id"] == church_id), None)
    if not church:
        return jsonify({"error": "Church not found"}), 404

    if not data.get('name'):
        return jsonify({"error": "New name is required"}), 400

    church["name"] = data["name"]
    save_locations(locations)
    return jsonify({"message": "Church updated successfully", "church": church})


# ===================== DELETE ROUTES =====================
@locations_bp.route('/stations/<int:station_id>', methods=['DELETE'])
def delete_station(station_id):
    """Delete a station"""
    locations = load_locations()
    station = next((s for s in locations["stations"] if s["id"] == station_id), None)

    if not station:
        return jsonify({"error": "Station not found"}), 404

    locations["stations"].remove(station)
    save_locations(locations)
    return jsonify({"message": "Station deleted successfully"})


@locations_bp.route('/stations/<int:station_id>/districts/<int:district_id>', methods=['DELETE'])
def delete_district(station_id, district_id):
    """Delete a district"""
    locations = load_locations()

    station = next((s for s in locations["stations"] if s["id"] == station_id), None)
    if not station:
        return jsonify({"error": "Station not found"}), 404

    district = next((d for d in station["districts"] if d["id"] == district_id), None)
    if not district:
        return jsonify({"error": "District not found"}), 404

    station["districts"].remove(district)
    save_locations(locations)
    return jsonify({"message": "District deleted successfully"})


@locations_bp.route('/stations/<int:station_id>/districts/<int:district_id>/churches/<int:church_id>', methods=['DELETE'])
def delete_church(station_id, district_id, church_id):
    """Delete a church"""
    locations = load_locations()

    station = next((s for s in locations["stations"] if s["id"] == station_id), None)
    if not station:
        return jsonify({"error": "Station not found"}), 404

    district = next((d for d in station["districts"] if d["id"] == district_id), None)
    if not district:
        return jsonify({"error": "District not found"}), 404

    church = next((c for c in district["churches"] if c["id"] == church_id), None)
    if not church:
        return jsonify({"error": "Church not found"}), 404

    district["churches"].remove(church)
    save_locations(locations)
    return jsonify({"message": "Church deleted successfully"})
