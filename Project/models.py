from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy



db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    profile_pic = db.Column(db.Text)
    password = db.Column(db.String, nullable=False)

    cars = db.relationship('Car', backref='owner')    

class Car(db.Model):
    __tablename__ = 'cars'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vin = db.Column(db.String, nullable=False)

    car_info = db.relationship('CarInfo', backref='car')

class CarInfo(db.Model):
    __tablename__ = 'car_info'

    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    make = db.Column(db.String, nullable=False)
    model = db.Column(db.String, nullable=False)
    trim = db.Column(db.String)
    top_speed = db.Column(db.Integer)
    cylinders = db.Column(db.String)
    horsepower = db.Column(db.String)
    turbo = db.Column(db.String)
    engine_model = db.Column(db.String)
    fuel_type = db.Column(db.String)
    transmission_style = db.Column(db.String)
    drive_type = db.Column(db.String)

def connect_db(app):
    db.app = app
    db.init_app(app)