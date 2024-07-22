import os
import pytest
from app import app, db
from models import User, Car, CarInfo, fetch_car_data, save_car_data
import requests 


@pytest.fixture(scope='module')
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///car_lookup'
    app.config['WTF_CSRF_ENABLED'] = False  
    app.config['SECRET_KEY'] = 'testsecretkey'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()
            
@pytest.fixture(scope='module')
def init_database(client):
    with app.app_context():
        user = User.register(name='TestUser', email='test@example.com', profile_pic='', password='password')
        db.session.add(user)
        db.session.commit()
        
        yield db

        db.session.remove()
        db.drop_all()


def test_user_registration(init_database):
    """Test User registration"""
    with app.app_context():
        user = User.query.filter_by(email="test@example.com").first()
        assert user is not None
        assert user.name == "TestUser"
        assert user.email == "test@example.com"

def test_user_authentication(init_database):
    """Test User authentication"""
    with app.app_context():
        user = User.authenticate(email="test@example.com", password="password")
        assert user is not None
        assert user.email == "test@example.com"

        invalid_user = User.authenticate(email="wrong@example.com", password="password")
        assert invalid_user is False

        invalid_password = User.authenticate(email="test@example.com", password="wrongpassword")
        assert invalid_password is False


def test_fetch_car_data(monkeypatch):
    """Test Car data fetching"""
    sample_vin_data = {
        "Results": [
            {"Variable": "Model Year", "Value": "2020"},
            {"Variable": "Make", "Value": "Toyota"},
            {"Variable": "Model", "Value": "Corolla"},
            {"Variable": "Trim", "Value": "LE"},
            {"Variable": "Top Speed", "Value": "120"},
            {"Variable": "Engine Number of Cylinders", "Value": "4"},
            {"Variable": "Engine HP", "Value": "130"},
            {"Variable": "Turbo", "Value": "No"},
            {"Variable": "Engine Model", "Value": "1.8L"},
            {"Variable": "Fuel Type - Primary", "Value": "Gasoline"},
            {"Variable": "Transmission Style", "Value": "Automatic"},
            {"Variable": "Drive Type", "Value": "FWD"}
        ]
    }

    def mock_requests_get(*args, **kwargs):
        class MockResponse:
            def json(self):
                return sample_vin_data
        return MockResponse()

    monkeypatch.setattr(requests, 'get', mock_requests_get)
    vin = "1HGCM82633A123456"
    car_info_data = fetch_car_data(vin)

    assert car_info_data['year'] == 2020
    assert car_info_data['make'] == "Toyota"
    assert car_info_data['model'] == "Corolla"
    assert car_info_data['trim'] == "LE"
    assert car_info_data['top_speed'] == 120
    assert car_info_data['cylinders'] == "4"
    assert car_info_data['horsepower'] == "130"
    assert car_info_data['turbo'] == "No"
    assert car_info_data['engine_model'] == "1.8L"
    assert car_info_data['fuel_type'] == "Gasoline"
    assert car_info_data['transmission_style'] == "Automatic"
    assert car_info_data['drive_type'] == "FWD"


def test_save_car_data(init_database):
    """Test saving car data"""
    with app.app_context():
        user = User.query.filter_by(email="test@example.com").first()
        vin = "1HGCM82633A123456"
        car_info_data = {
            "year": 2020,
            "make": "Toyota",
            "model": "Corolla",
            "trim": "LE",
            "top_speed": 120,
            "cylinders": "4",
            "horsepower": "130",
            "turbo": "No",
            "engine_model": "1.8L",
            "fuel_type": "Gasoline",
            "transmission_style": "Automatic",
            "drive_type": "FWD"
        }
        save_car_data(vin, user.id, car_info_data)

        car = Car.query.filter_by(vin=vin).first()
        assert car is not None
        assert car.vin == vin
        assert car.owner.id == user.id

        car_info = CarInfo.query.filter_by(car_id=car.id).first()
        assert car_info is not None
        assert car_info.year == 2020
        assert car_info.make == "Toyota"
        assert car_info.model == "Corolla"
        assert car_info.trim == "LE"
        assert car_info.top_speed == 120
        assert car_info.cylinders == "4"
        assert car_info.horsepower == "130"
        assert car_info.turbo == "No"
        assert car_info.engine_model == "1.8L"
        assert car_info.fuel_type == "Gasoline"
        assert car_info.transmission_style == "Automatic"
        assert car_info.drive_type == "FWD"
