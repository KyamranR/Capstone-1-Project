from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, IntegerField, BooleanField, SelectField
from wtforms.validators import InputRequired, Length, DataRequired, Email, Optional


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


class EditUserProfileForm(FlaskForm):
    """Editing user profile"""

    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    profile_pic = StringField('Profile Photo')


class EditCarInfoForm(FlaskForm):
    """Editing car information"""

    year = IntegerField('Year', validators=[Optional()])
    make = StringField('Make', validators=[Optional()])
    model = StringField('Model', validators=[Optional()])
    trim = StringField('Trim', validators=[Optional()])
    top_speed = IntegerField('Top Speed', validators=[Optional()])
    cylinders = IntegerField('Cylinders', validators=[Optional()])
    horsepower = IntegerField('Horsepower', validators=[Optional()])
    turbo = SelectField('Turbo', choices=[('True', 'True'), ('False', 'False')], validators=[Optional()])
    engine_model = StringField('Engine Model', validators=[Optional()])
    transmission_style = StringField('Transmission Style', validators=[Optional()])
    drive_type = StringField('Drive Type', validators=[Optional()])
    