from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy_serializer import SerializerMixin 


db = SQLAlchemy()


class Station(db.Model, SerializerMixin):
    __tablename__ = 'stations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    districts = db.relationship('District', backref='station', cascade='all, delete-orphan')


class District(db.Model, SerializerMixin):
    __table__ = 'districts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    station_id = db.Column(db.Integer, db.ForeignKey('stations.id'), nullable=False)

    churches = db.relationship('Church', backref='district', cascade='all, delete-orphan')


class Church(db.Model, SerializerMixin):
    __tablename__ = 'churches'
    id = db.Clumn(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    district_id = db.Column(db.Integer, db.ForeignKey('districts.id'), nullable=False)