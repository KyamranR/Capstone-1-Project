import os
from flask import Flask, render_template, request, flash, redirect, session, url_for
from models import db, connect_db, User, Car, CarInfo, fetch_data
from form import LoginForm, RegistrationFrom



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///car_lookup'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")

connect_db(app)
with app.app_context():
    db.create_all()



@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/get-car-info', methods=['POST'])
def get_car_info():
    vin = request.form['vin'].upper()
    user_id = session.get('user_id')
    if user_id:
        flash("You must be logged in to add a car.", "danger")
        return redirect(url_for('index'))
    
    car = Car.query.filter_by(vin=vin).first()

    if not car:
        fetch_data(vin, user_id=1)
        car = Car.query.filter_by(vin=vin).first()

    car_info = CarInfo.query.filter_by(car_id=car.id).first()
    return render_template('car_info.html', car_info=car_info, user_id=user_id)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register form for users"""

    form = RegistrationFrom()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        profile_pic = form.profile_pic.data
        password = form.password.data

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('User already exists. Please choose different email.', 'error')
            return redirect('/register')

        new_user = User.register(name, email, profile_pic, password)
        db.session.add(new_user)
        db.session.commit()
        session['email'] = new_user.email
        return redirect(url_for('index', email=session['email']))

    return render_template('register.html', form=form)
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login form for users"""
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.authenticate(email, password)

        if user:
            session['email'] = user.email
            flash('Logged In Successfully', 'success')
            return redirect(url_for('index'))
        else:
            form.email.errors = ['Invalid email/password.']

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('email')
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))