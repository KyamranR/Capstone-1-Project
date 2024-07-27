from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, Email, Optional


class LoginForm(FlaskForm):
    """User login form"""

    email = StringField('Email:', validators=[DataRequired()], render_kw={'placeholder': 'Enter email'})
    password = PasswordField('Password:', validators=[DataRequired()], render_kw={'placeholder': 'Enter password'})



class RegistrationForm(FlaskForm):
    """User registration form"""

    name = StringField('Name:', validators=[DataRequired(), Length(min=1, max=20)], render_kw={'placeholder': 'Enter your full name'})
    email = StringField('Email:', validators=[DataRequired(), Length(max=50)], render_kw={'placeholder': 'Enter your email (required)'})
    profile_pic = StringField('Profile Photo', render_kw={'placeholder': '(Optional)'})
    password = PasswordField('Password:', validators=[DataRequired(), Length(min=6, max=50)], render_kw={'placeholder': 'Password'})


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
    