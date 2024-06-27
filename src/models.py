from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)
    
    favorites = db.relationship('Favorites', backref='user', lazy=True)

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
        }

class People(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=False, nullable=False)
    gender = db.Column(db.String(50), unique=False, nullable=False)
    
    favorites = db.relationship('Favorites', backref='people', lazy=True)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender
        }

class Planets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=False, nullable=False)
    population = db.Column(db.Integer, unique=False, nullable=False)
    
    favorites = db.relationship('Favorites', backref='planets', lazy=True)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "population": self.population
        }

class Favorites(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    people_id = db.Column(db.Integer, ForeignKey('people.id'), nullable=True)
    planet_id = db.Column(db.Integer, ForeignKey('planets.id'), nullable=True)

    def __init__(self, user_id, people_id=None, planet_id=None):
        self.user_id = user_id
        self.people_id = people_id
        self.planet_id = planet_id

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "people_id": self.people_id,
            "planet_id": self.planet_id
        }
