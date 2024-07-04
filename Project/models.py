from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
import requests


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

    @classmethod
    def register(cls, name, email, profile_pic, password):
        """Register user with hashed password"""
        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode('utf8')
        
        return cls(name=name, email=email, profile_pic=profile_pic, password=hashed_utf8)
    
    @classmethod
    def authenticate(cls, email, password):
        """Validate that user exists and password is correct"""
        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False  

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




def fetch_data(vin, user_id):
    """Get data from API"""

    url = f'https://vpic.nhtsa.dot.gov/api/vehicles/decodevin/{vin}?format=json'
    response = requests.get(url)
    data = response.json()

    car_info_data = {}
    for item in data['Results']:
        if item['Variable'] == 'Model Year':
            car_info_data['year'] = int(item['Value']) if item['Value'] else None
        elif item['Variable'] == 'Make':
            car_info_data['make'] = item['Value']
        elif item['Variable'] == 'Model':
            car_info_data['model'] = item['Value']
        elif item['Variable'] == 'Trim':
            car_info_data['trim'] = item['Value']
        elif item['Variable'] == 'Top Speed':
            car_info_data['top_speed'] = int(item['Value']) if item['Value'] else None
        elif item['Variable'] == 'Engine Number of Cylinders':
            car_info_data['cylinders'] = item['Value']
        elif item['Variable'] == 'Engine HP':
            car_info_data['horsepower'] = item['Value']
        elif item['Variable'] == 'Turbo':
            car_info_data['turbo'] = item['Value']
        elif item['Variable'] == 'Engine Model':
            car_info_data['engine_model'] = item['Value']
        elif item['Variable'] == 'Fuel Type - Primary':
            car_info_data['fuel_type'] = item['Value']
        elif item['Variable'] == 'Transmission Style':
            car_info_data['transmission_style'] = item['Value']
        elif item['Variable'] == 'Drive Type':
            car_info_data['drive_type'] = item['Value']

    car = Car(vin=vin, user_id=user_id)
    db.session.add(car)
    db.session.commit()

    car_info = CarInfo(
        car_id=car.id,
        year=car_info_data.get('year'),
        make=car_info_data.get('make'),
        model=car_info_data.get('model'),
        trim=car_info_data.get('trim'),
        top_speed=car_info_data.get('top_speed'),
        cylinders=car_info_data.get('cylinders'),
        horsepower=car_info_data.get('horsepower'),
        turbo=car_info_data.get('turbo'),
        engine_model=car_info_data.get('engine_model'),
        fuel_type=car_info_data.get('fuel_type'),
        transmission_style=car_info_data.get('transmission_style'),
        drive_type=car_info_data.get('drive_type')
    )
    db.session.add(car_info)
    db.session.commit()

def connect_db(app):
    db.app = app
    db.init_app(app)