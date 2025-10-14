from flask import Flask 
from flask_cors import CORS 
from flask_migrate import Migrate 
from models import db 
from config import Config 
from routes.locations import locations_bp 


app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(locations_bp)

@app.route('/')
def home():
    return {"message": "Welcome to the Locations API"}


if __name__ == '__main__':
    app.run(debug=True)