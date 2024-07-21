import pytest
from app import app
from form import LoginForm, RegistrationForm, EditUserProfileForm, EditCarInfoForm

@pytest.fixture(scope='module')
def test_client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  
    app.config['SECRET_KEY'] = 'testsecretkey' 

    with app.test_client() as client:
        with app.app_context():
            yield client

def test_login_form(test_client):
    """Test the login form validation"""
    with app.app_context():
        form = LoginForm(
            email="test@example.com",
            password="password"
        )
        assert form.validate() == True

        form = LoginForm(
            email="",
            password="password"
        )
        assert form.validate() == False

        form = LoginForm(
            email="test@example.com",
            password=""
        )
        assert form.validate() == False

def test_registration_form(test_client):
    """Test the registration form validation"""
    with app.app_context():
        form = RegistrationForm(
            name="TestUser",
            email="test@example.com",
            profile_pic="",
            password="password"
        )
        assert form.validate() == True

        form = RegistrationForm(
            name="",
            email="test@example.com",
            profile_pic="",
            password="password"
        )
        assert form.validate() == False

        form = RegistrationForm(
            name="TestUser",
            email="",
            profile_pic="",
            password="password"
        )
        assert form.validate() == False

        form = RegistrationForm(
            name="TestUser",
            email="test@example.com",
            profile_pic="",
            password=""
        )
        assert form.validate() == False

        form = RegistrationForm(
            name="TestUser",
            email="test@example.com",
            profile_pic="",
            password="short"
        )
        assert form.validate() == False

def test_edit_user_profile_form(test_client):
    """Test the edit user profile form validation"""
    with app.app_context():
        form = EditUserProfileForm(
            name="Updated User",
            email="updated@example.com",
            profile_pic="https://profile-pic.com"
        )
        assert form.validate() == True

        form = EditUserProfileForm(
            name="",
            email="updated@example.com",
            profile_pic="https://profile-pic.com"
        )
        assert form.validate() == False

        form = EditUserProfileForm(
            name="Updated User",
            email="",
            profile_pic="https://profile-pic.com"
        )
        assert form.validate() == False

        form = EditUserProfileForm(
            name="Updated User",
            email="not-an-email",
            profile_pic="https://profile-pic.com"
        )
        assert form.validate() == False

def test_edit_car_info_form(test_client):
    """Test the edit car info form validation"""
    with app.app_context():
        form = EditCarInfoForm(
            year=2020,
            make="Toyota",
            model="Corolla",
            trim="LE",
            top_speed=120,
            cylinders=4,
            horsepower=130,
            turbo="True",
            engine_model="1.8L",
            transmission_style="Automatic",
            drive_type="FWD"
        )
        assert form.validate() == True

        form = EditCarInfoForm(
            year=None,
            make=None,
            model=None,
            trim=None,
            top_speed=None,
            cylinders=None,
            horsepower=None,
            turbo=None,
            engine_model=None,
            transmission_style=None,
            drive_type=None
        )
        assert form.validate() == True