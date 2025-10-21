from flask import Blueprint, request, jsonify, session
from config import db, app
from models import Admin
from flask_bcrypt import Bcrypt
from functools import wraps
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

bcrypt = Bcrypt(app)
admin_auth_bp = Blueprint('admin_auth', __name__)

# Serializer for password reset tokens
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])


# --------------- Helpers -----------------
def login_required(f):
    """Restrict access to logged-in admins"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return jsonify({"error": "Unauthorized. Please log in."}), 401
        return f(*args, **kwargs)
    return decorated_function


def super_admin_required(f):
    """Restrict access to super admin only"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        admin_id = session.get('admin_id')

        if not admin_id:
            return jsonify({"error": "Unauthorized. Please log in."}), 401

        admin = Admin.query.get(admin_id)
        if not admin or not admin.is_super_admin:
            return jsonify({"error": "Forbidden. Super admin access only."}), 403
        return f(*args, **kwargs)
    return decorated_function


# --------------- AUTH Routes -----------------

# Admin Login
@admin_auth_bp.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    admin = Admin.query.filter_by(email=email).first()
    if not admin or not bcrypt.check_password_hash(admin.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401

    if not admin.is_active:
        return jsonify({"error": "Account is deactivated. Contact your super admin."}), 403

    session['admin_id'] = admin.id
    session['is_super_admin'] = admin.is_super_admin
    return jsonify({
        "message": "Login successful",
        "admin": admin.serialize()
    }), 200


# Admin Logout
@admin_auth_bp.route('/admin/logout', methods=['POST'])
@login_required
def admin_logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200


# View Admin Profile
@admin_auth_bp.route('/admin/profile', methods=['GET'])
@login_required
def admin_profile():
    admin_id = session.get('admin_id')
    admin = Admin.query.get(admin_id)

    if not admin:
        return jsonify({"error": "Admin not found"}), 404

    return jsonify(admin.serialize()), 200


# --------------- SUPER ADMIN ROUTES -----------------

# Create New Admin
@admin_auth_bp.route('/admin/create', methods=['POST'])
@super_admin_required
def create_admin():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    if not all([username, email, password, confirm_password]):
        return jsonify({"error": "All fields are required"}), 400

    if password != confirm_password:
        return jsonify({"error": "Passwords do not match"}), 400

    if Admin.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400

    new_admin = Admin(
        username=username,
        email=email,
        is_super_admin=False,
        is_active=True
    )
    new_admin.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    db.session.add(new_admin)
    db.session.commit()

    return jsonify({
        "message": "New admin created successfully",
        "admin": new_admin.serialize()
    }), 201


# View All Admins
@admin_auth_bp.route('/admin/all', methods=['GET'])
@super_admin_required
def get_all_admins():
    admins = Admin.query.all()
    return jsonify([admin.serialize() for admin in admins]), 200


# Deactivate or Reactivate Admin
@admin_auth_bp.route('/admin/toggle/<int:admin_id>', methods=['PATCH'])
@super_admin_required
def toggle_admin(admin_id):
    admin = Admin.query.get(admin_id)

    if not admin:
        return jsonify({"error": "Admin not found"}), 404

    if admin.is_super_admin:
        return jsonify({"error": "Cannot deactivate the super admin"}), 403

    admin.is_active = not admin.is_active
    db.session.commit()

    status = "activated" if admin.is_active else "deactivated"
    return jsonify({"message": f"Admin {status} successfully"}), 200


# Delete Admin
@admin_auth_bp.route('/admin/delete/<int:admin_id>', methods=['DELETE'])
@super_admin_required
def delete_admin(admin_id):
    admin = Admin.query.get(admin_id)

    if not admin:
        return jsonify({"error": "Admin not found"}), 404

    if admin.is_super_admin:
        return jsonify({"error": "Cannot delete the super admin"}), 403

    db.session.delete(admin)
    db.session.commit()

    return jsonify({"message": "Admin deleted successfully"}), 200


# ----------------- Password Management -----------------

# Super Admin resets another Admin's password
@admin_auth_bp.route('/admin/reset_password/<int:admin_id>', methods=['PUT'])
@super_admin_required
def super_reset_password(admin_id):
    admin = Admin.query.get(admin_id)

    if not admin:
        return jsonify({"error": "Admin not found"}), 404

    data = request.get_json()
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')

    if not all([new_password, confirm_password]):
        return jsonify({"error": "Both password fields are required"}), 400

    if new_password != confirm_password:
        return jsonify({"error": "Passwords do not match"}), 400

    admin.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
    db.session.commit()

    return jsonify({"message": f"Password updated for {admin.username}"}), 200


# Admin changes own password (requires old password)
@admin_auth_bp.route('/admin/change_password', methods=['PUT'])
@login_required
def change_own_password():
    admin = Admin.query.get(session['admin_id'])
    data = request.get_json()

    old_password = data.get('old_password')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')

    if not all([new_password, confirm_password]):
        return jsonify({"error": "New password and confirmation required"}), 400

    if new_password != confirm_password:
        return jsonify({"error": "Passwords do not match"}), 400

    if old_password and not bcrypt.check_password_hash(admin.password_hash, old_password):
        return jsonify({"error": "Old password is incorrect"}), 401

    admin.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
    db.session.commit()

    return jsonify({"message": "Password changed successfully"}), 200


# ----------------- Forgot Password -----------------

@admin_auth_bp.route('/admin/forgot_password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')

    admin = Admin.query.filter_by(email=email).first()
    if not admin:
        return jsonify({"error": "Email not found"}), 404

    token = serializer.dumps(email, salt='password-reset-salt')
    reset_link = f"http://localhost:5000/admin/reset_password/{token}"

    # For dev: print reset link to console
    print(f"Password reset link: {reset_link}")

    return jsonify({"message": "Password reset link generated (check console)"}), 200


@admin_auth_bp.route('/admin/reset_password/<token>', methods=['POST'])
def reset_password(token):
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=3600)
    except SignatureExpired:
        return jsonify({"error": "Token expired"}), 400
    except BadSignature:
        return jsonify({"error": "Invalid token"}), 400

    data = request.get_json()
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')

    if not all([new_password, confirm_password]):
        return jsonify({"error": "Both password fields required"}), 400

    if new_password != confirm_password:
        return jsonify({"error": "Passwords do not match"}), 400

    admin = Admin.query.filter_by(email=email).first()
    if not admin:
        return jsonify({"error": "Admin not found"}), 404

    admin.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
    db.session.commit()

    return jsonify({"message": "Password reset successfully"}), 200

