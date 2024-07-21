import pytest
from app import app, db
from models import User, Car, CarInfo
from flask import session
from werkzeug.security import check_password_hash
from unittest.mock import patch

@pytest.fixture(scope='module')
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///car_lookup'
    app.config['WTF_CSRF_ENABLED'] = False  

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()


@pytest.fixture(scope='module')
def init_database():
    db.create_all()
    user = User(name='TestUser', email='test@email.com', password='password')
    db.session.add(user)
    db.session.commit()

    yield db

    db.session.remove()
    db.drop_all()


def test_register(client):
    """Testing registration of new user"""
    response = client.post('/register', data=dict(
        name='New User',
        email='new@test.com',
        profile_pic='',
        password='newpassword',
        confirm_password='newpassword'
    ), follow_redirects=True)

    assert response.status_code == 200
    assert b'Registered successfully!' in response.data
    user = User.query.filter_by(email='new@test.com').first()
    assert user is not None


def test_login(client, init_database):
    """Testing if user can login"""
    response = client.post('/login', data=dict(
        email='test@email.com',
        password='password'
    ), follow_redirects=True)

    assert response.status_code == 200
    assert b'Logged In Successfully' in response.data
    assert session['user_id'] == 1

def test_logout(client, init_database):
    """Testing if user can logout"""
    client.post('/login', data=dict(
        email='test@email.com',
        password='password'
    ), follow_redirects=True)
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Logged out successfully' in response.data
    assert 'user_id' not in session

def test_user_profile(client, init_database):
    """Testing if user profile shows user's name"""
    client.post('/login', data=dict(
        email='test@email.com',
        password='password'
    ), follow_redirects=True)
    response = client.get('/user/1')
    assert response.status_code == 200
    assert b'TestUser' in response.data

def test_update_user_profile(client, init_database):
    """Testing if user can update thier info"""
    client.post('/login', data=dict(
        email='test@email.com',
        password='password'
    ), follow_redirects=True)
    response = client.post('/user/1/update', data=dict(
        name='Updated User',
        email='updated@test.com',
        profile_pic='https://profile-pic.com'
    ), follow_redirects=True)

    assert response.status_code == 200
    assert b'User info was updated successfully!' in response.data
    user = User.query.get(1)
    assert user.name == 'Updated User'
    assert user.email == 'updated@test.com'

def test_get_car_info(client):
    """Testing if you get redirected after entering vin"""
    response = client.post('/get-car-info', data=dict(
        vin='2T3W1RFV3PW284566'
    ), follow_redirects=True)

    assert response.status_code == 200

def test_get_car_info_vin_not_provided(client, init_database):
    """Test if VIN is not provided."""
    response = client.post('/get-car-info/', data=dict(
        vin=''
    ), follow_redirects=True)
    assert response.status_code == 200
    assert b'VIN is required.' in response.data

@patch('app.fetch_car_data')
def test_get_car_info_vin_provided_car_not_in_db(mock_fetch_car_data, client, init_database):
    """Test if VIN is provided but car does not exist in the database."""
    mock_fetch_car_data.return_value = {
        'year': '2023',
        'make': 'Toyota',
        'model': 'Rav4',
        'trim': 'XLE',
        'top_speed': 120,
        'cylinders': 4,
        'horsepower': 280,
        'turbo': False,
        'engine_model': 'K2-JZ',
        'transmission_style': 'Automatic',
        'drive_type': '2x4'
    }

    response = client.post('/get-car-info/', data=dict(
        vin='2T3W1RFV3PW284566'
    ), follow_redirects=True)
    assert response.status_code == 200
    assert b'2023' in response.data
    assert b'Toyota' in response.data
    assert b'Rav4' in response.data
    assert b'XLE' in response.data

def test_get_car_info_vin_provided_car_in_db(client, init_database):
    """Test if VIN is provided and car already exists in the database."""
    user = User.query.filter_by(email='test@email.com').first()
    car = Car(vin='2T3W1RFV3PW284566', user_id=user.id)
    db.session.add(car)
    db.session.commit()

    car_info = CarInfo(
        car_id=car.id,
        year='2023',
        make='Toyota',
        model='Rav4',
        trim='XLE',
        top_speed=120,
        cylinders=4,
        horsepower=280,
        turbo=False,
        engine_model='K2-JZ',
        transmission_style='Automatic',
        drive_type='2x4'
    )

    db.session.add(car_info)
    db.session.commit()

    response = client.post('/get-car-info/', data=dict(
        vin='2T3W1RFV3PW284566'
    ), follow_redirects=True)
    assert response.status_code == 200
    assert b'2023' in response.data
    assert b'Toyota' in response.data
    assert b'Rav4' in response.data
    assert b'XLE' in response.data
    assert b'120' in response.data
    assert b'4' in response.data
    assert b'280' in response.data
    assert b'K2-JZ' in response.data
    assert b'Automatic' in response.data
    assert b'2x4' in response.data

def test_show_car_info(client, init_database):
    """Testing if car info shows up when user is logged in"""
    response = client.post('/login', data=dict(
        email='test@email.com',
        password='password'
    ), follow_redirects=True)

    assert response.status_code == 200

    user = User.query.filter_by(email='test@email.com').first()
    car = Car(vin='2T3W1RFV3PW284566', user_id=user.id)
    db.session.add(car)
    db.session.commit()

    car_info = CarInfo(
        car_id=car.id,
        year='2023',
        make='Toyota',
        model='Rav4',
        trim='XLE',
        top_speed=120,
        cylinders=4,
        horsepower=280,
        turbo=False,
        engine_model='K2-JZ',
        transmission_style='Automatic',
        drive_type='2x4'
    )

    db.session.add(car_info)
    db.session.commit()

    response = client.get(f'/show-car-info/{car.vin}')
    assert response.status_code == 200
    assert b'2023' in response.data
    assert b'Toyota' in response.data
    assert b'Rav4' in response.data
    assert b'XLE' in response.data
    assert b'120' in response.data
    assert b'4' in response.data
    assert b'280' in response.data
    assert b'K2-JZ' in response.data
    assert b'Automatic' in response.data
    assert b'2x4' in response.data


def test_show_car_info_not_logged_in(client):
    """Testing if user can check car info when not logged in"""

    response= client.get('/show-car-info/2T3W1RFV3PW284566', follow_redirects=True)
    assert response.status_code == 200
    assert b'User not logged in.' in response.data
    assert b'Login' in response.data

def test_show_car_info_car_not_found(client, init_database):
    """Testing if car not found it displays correct message"""

    response = client.get('/login', data=dict(
        email='test@email.com',
        password='password'
    ), follow_redirects=True)

    assert response.status_code == 200

    response = client('/show-car-info/2T3W1RFV3PW284566', follow_redirects=True)
    assert response.status_code == 200
    assert b'Car not found.' in response.data

def test_show_car_info_car_info_not_found(client, init_database):
    """Testing if car info returns not found"""

    response = client.post('/login', data=dict(
        email='test@email.com',
        password='password'
    ), follow_redirects=True)
    assert response.status_code == 200

    user = User.query.filter_by(email='test@email.com').first()
    car = Car(vin='2T3W1RFV3PW284566', user_id=user.id)
    db.session.add(car)
    db.session.commit()

    response = client.get('/show-car-info/2T3W1RFV3PW284566', follow_redirects=True)
    assert response.status_code == 200
    assert b'Car info could not be found.' in response.data

def test_update_car_info_not_logged_in(client, init_database):
    """Test if user is not logged in."""
    response = client.get('/update-car-info/2T3W1RFV3PW284566', follow_redirects=True)
    assert response.status_code == 200
    assert b'User not logged in.' in response.data

def test_update_car_info_car_not_found(client, init_database):
    """Test if car is not found for the logged-in user."""
    client.post('/login', data=dict(
        email='test@email.com',
        password='password'
    ), follow_redirects=True)

    response = client.get('/update-car-info/2T3W1RFV3PW284566', follow_redirects=True)
    assert response.status_code == 200
    assert b'Car not found.' in response.data

def test_update_car_info_car_info_not_found(client, init_database):
    """Test if car info is not found for the car."""
    user = User.query.filter_by(email='test@email.com').first()
    car = Car(vin='2T3W1RFV3PW284566', user_id=user.id)
    db.session.add(car)
    db.session.commit()

    response = client.get('/update-car-info/2T3W1RFV3PW284566', follow_redirects=True)
    assert response.status_code == 200
    assert b'Car information not found.' in response.data

def test_update_car_info_successful(client, init_database):
    """Test successful update of car information."""
    user = User.query.filter_by(email='test@email.com').first()
    car = Car(vin='2T3W1RFV3PW284566', user_id=user.id)
    db.session.add(car)
    db.session.commit()

    car_info = CarInfo(
        car_id=car.id,
        year='2023',
        make='Toyota',
        model='Rav4',
        trim='XLE',
        top_speed=120,
        cylinders=4,
        horsepower=280,
        turbo=False,
        engine_model='K2-JZ',
        transmission_style='Automatic',
        drive_type='2x4'
    )
    db.session.add(car_info)
    db.session.commit()

    response = client.post(f'/update-car-info/{car.vin}', data=dict(
        year='2024',
        make='Toyota',
        model='Rav4',
        trim='Limited',
        top_speed=130,
        cylinders=6,
        horsepower=300,
        turbo=True,
        engine_model='K2-JZ',
        transmission_style='Automatic',
        drive_type='4x4'
    ), follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Car information updated successfully.' in response.data
    car_info = CarInfo.query.filter_by(car_id=car.id).first()
    assert car_info.year == '2024'
    assert car_info.trim == 'Limited'
    assert car_info.top_speed == 130
    assert car_info.cylinders == 6
    assert car_info.horsepower == 300
    assert car_info.turbo is True

@patch('app.db.session.commit')
def test_update_car_info_failed_update(mock_db_commit, client, init_database):
    """Test failed update due to a database error."""
    mock_db_commit.side_effect = Exception('Database commit failed')

    user = User.query.filter_by(email='test@email.com').first()
    car = Car(vin='2T3W1RFV3PW284566', user_id=user.id)
    db.session.add(car)
    db.session.commit()

    car_info = CarInfo(
        car_id=car.id,
        year='2023',
        make='Toyota',
        model='Rav4',
        trim='XLE',
        top_speed=120,
        cylinders=4,
        horsepower=280,
        turbo=False,
        engine_model='K2-JZ',
        transmission_style='Automatic',
        drive_type='2x4'
    )
    db.session.add(car_info)
    db.session.commit()

    response = client.post(f'/update-car-info/{car.vin}', data=dict(
        year='2024',
        make='Toyota',
        model='Rav4',
        trim='Limited',
        top_speed=130,
        cylinders=6,
        horsepower=300,
        turbo=True,
        engine_model='K2-JZ',
        transmission_style='Automatic',
        drive_type='4x4'
    ), follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Error updating car information. Please try again.' in response.data

def test_remove_car_not_logged_in(client, init_database):
    """Test if user is not logged in."""
    response = client.post('/remove-car/1', follow_redirects=True)
    assert response.status_code == 200
    assert b'You are not authorized to delete the car.' in response.data

def test_remove_car_not_authorized(client, init_database):
    """Test if user is not authorized to delete the car."""
    client.post('/login', data=dict(
        email='test@email.com',
        password='password'
    ), follow_redirects=True)

    # Create another user to simulate unauthorized access
    other_user = User(name='OtherUser', email='other@email.com', password='password')
    db.session.add(other_user)
    db.session.commit()

    car = Car(vin='2T3W1RFV3PW284566', user_id=other_user.id)
    db.session.add(car)
    db.session.commit()

    response = client.post(f'/remove-car/{car.id}', follow_redirects=True)
    assert response.status_code == 200
    assert b'You are not authorized to delete the car.' in response.data

def test_remove_car_not_found(client, init_database):
    """Test if car is not found."""
    client.post('/login', data=dict(
        email='test@email.com',
        password='password'
    ), follow_redirects=True)

    response = client.post('/remove-car/9999', follow_redirects=True)
    assert response.status_code == 404

def test_remove_car_successful(client, init_database):
    """Test successful car removal."""
    client.post('/login', data=dict(
        email='test@email.com',
        password='password'
    ), follow_redirects=True)

    user = User.query.filter_by(email='test@email.com').first()
    car = Car(vin='2T3W1RFV3PW284566', user_id=user.id)
    db.session.add(car)
    db.session.commit()

    response = client.post(f'/remove-car/{car.id}', follow_redirects=True)
    assert response.status_code == 200
    assert b'Car removed successfully!' in response.data
    assert Car.query.get(car.id) is None

@patch('app.db.session.commit')
def test_remove_car_failed(mock_db_commit, client, init_database):
    """Test failed car removal due to a database error."""
    mock_db_commit.side_effect = Exception('Database commit failed')

    client.post('/login', data=dict(
        email='test@email.com',
        password='password'
    ), follow_redirects=True)

    user = User.query.filter_by(email='test@email.com').first()
    car = Car(vin='2T3W1RFV3PW284566', user_id=user.id)
    db.session.add(car)
    db.session.commit()

    response = client.post(f'/remove-car/{car.id}', follow_redirects=True)
    assert response.status_code == 200
    assert b'Error removing car. Please try again.' in response.data
    assert Car.query.get(car.id) is not None