from config import db 
from datetime import datetime 

# _______________ LOCATION MODELS _______________

class Station(db.Model, SerializerMixin):
    __tablename__ = 'stations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    districts = db.relationship('District', backref='station', cascade='all, delete-orphan')


class District(db.Model, SerializerMixin):
    __tablename__ = 'districts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    station_id = db.Column(db.Integer, db.ForeignKey('stations.id'), nullable=False)

    churches = db.relationship('Church', backref='district', cascade='all, delete-orphan')


class Church(db.Model, SerializerMixin):
    __tablename__ = 'churches'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    district_id = db.Column(db.Integer, db.ForeignKey('districts.id'), nullable=False)


# _______________ MEETING MODELS _______________
class Meeting(db.Model, SerializerMixin):
    __tablename__ = 'meetings'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)
    registration_amount = db.Column(db.Float, nullable=False)
    poster_url = db.Column(db.String(300))
    description = db.Column(db.Text)


class Registration(db.Model, SerializerMixin):
    __tablename__ = 'registrations'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    station = db.Column(db.String(100), nullable=False)
    district = db.Column(db.String(100), nullable=False)
    church = db.Column(db.String(100), nullable=False)
    leader_name = db.Column(db.String(120), nullable=False)
    leader_phone = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    invoice_number = db.Column(db.String(100), unique=True, nullable=False)
    paid = db.Column(db.Boolean, default=False)
    
    attendees = db.relationship('Attendee', backref='registration', cascade='all, delete-orphan')


class Attendee(db.Model, SerializerMixin):
    __tablename__ = 'attendees'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    registration_id = db.Column(db.Integer, db.ForeignKey('registration.id'))



# _______________ ADMIN MODELS _______________
class Admin(db.Model, SerializerMixin):
    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='admin') # 'admin' or 'super_admin'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


    # Exclude sensitive data from serialization
    serialize_rules = ('-password_hash',)

    # Password handling
    @property
    def password(self)
        raise AttributeError("password is write-only.")

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def is_super_admin(self):
        return self.role == 'super_admin'

    def __repr__(self):
        return f"<Admin {self.name} ({self.role})>"