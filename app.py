from flask import Flask 
from flask_cors import CORS 
from config import db, migrate, create_app
from routes.meeting import meeting_bp 
from routes.registration import registration_bp 
from routes.admin import admin_bp 
from routes.locations import locations_bp 
from routes.admin_auth import admin_auth_bp


app = create_app()
CORS(app)


# Register blueprints
app.register_blueprint(meeting_bp, url_prefix='/api')
app.register_blueprint(registration_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(locations_bp, url_prefix='/api')
app.register_blueprint(admin_auth_bp, url_prefix='/api/admin/auth')


if __name__ == '__main__':
    app.run(debug=True, port=5000)