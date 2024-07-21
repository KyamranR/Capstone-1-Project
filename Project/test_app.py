import pytest
from app import app, db
from models import User, Car, CarInfo
from flask import session
from werkzeug.security import check_password_hash

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
    response = client.post('/login', data=dict(
        email='test@email.com',
        password='password'
    ), follow_redirects=True)

    assert response.status_code == 200
    assert b'Logged In Successfully' in response.data
    assert session['user_id'] == 1

def test_logout(client, init_database):
    client.post('/login', data=dict(
        email='test@email.com',
        password='password'
    ), follow_redirects=True)
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Logged out successfully' in response.data
    assert 'user_id' not in session

def test_user_profile(client, init_database):
    client.post('/login', data=dict(
        email='test@email.com',
        password='password'
    ), follow_redirects=True)
    response = client.get('/user/1')
    assert response.status_code == 200
    assert b'TestUser' in response.data

def test_update_user_profile(client, init_database):
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
    response = client.post('/get-car-info', data=dict(
        vin='2T3W1RFV3PW284566'
    ), follow_redirects=True)

    assert response.status_code == 200

def test_show_car_info(client, init_database):
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


