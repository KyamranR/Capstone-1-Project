from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import InputRequired, Length


class LoginForm(FlaskForm):
    """User login form"""

    email = StringField('Email:', validators=[InputRequired()])
    password = PasswordField('Password:', validators=[InputRequired()])



class RegistrationFrom(FlaskForm):
    """User registration form"""

    name = StringField('Name:', validators=[InputRequired(), Length(min=1, max=20)])
    email = StringField('Email:', validators=[InputRequired(), Length(max=50)])
    profile_pic = StringField('Profile Photo')
    password = PasswordField('Password:', validators=[InputRequired(), Length(min=6, max=50)])