from flask import Blueprint, jsonify, send_file
import pandas as pd 
from io import BytesIO
from datetime import datetime
from routes.registration import load_registrations


admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/registrations', methods=['GET'])
def get_registrations():
    """Get all registrations (admin only)"""
    # In production, add authentication here
    registrations = load_registrations()
    return jsonify(registrations)

@admin_bp.route('/registrations/export', methods=['GET'])
def export_registrations():
    """Export registrations to Excel (admin only)"""
    # In production, add authentication here
    registrations = load_registrations()

    # Create DataFrame from registrations
    data = []
    for reg in registrations:
        for attendee in reg['attendees']:
            data.append({
                "Registration ID": reg['id'],
                "Invoice Number": reg['invoiceNumber'],
                "Station": reg['station'],
                "District": reg['district'],
                "Church": reg['church'],
                "Leader Name": reg['leaderName'],
                "Leader Phone": reg['leaderPhone'],
                "Attendee Name": attendee['name'],
                "Attendee Age": attendee['age'],
                "Amount": reg['amount'],
                "Paid": reg['paid'],
                "Registration Date": reg['timestamp']
            })
    df = pd.DataFrame(data)

    # Create Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Registrations', index=False)

    output.seek(0)

    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'registrations_{datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}.xlsx'
    )


@admin_bp.route('/summary', methods=['GET'])
def get_summary():
    """Get registration summary (admin only)"""
    # In production, add authentication here
    registrations = load_registrations()

    total_registrations = len(registrations)
    total_attendees = sum(len(reg['attendees']) for reg in registrations)
    total_amount = sum(reg['amount'] for reg in registrations)
    paid_amount = sum(reg['amount'] for reg in registrations if reg['paid'])

    # Count by station
    stations_count = {}
    for reg in registrations:
        station = reg['station']
        stations_count[station] = stations_count.get(station, 0) + len(reg['attendees'])

        return jsonify({
            "totalRegistrations": total_registrations,
            "totalAttendees": total_attendees,
            "totalAmount": total_amount,
            "paidAmount": paid_amount,
            "stationsBreakdown": stations_count
        })