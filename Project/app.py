import os
from flask import Flask, render_template, request, flash, redirect, session, url_for
from models import db, connect_db, User, Car, CarInfo, fetch_data
from form import LoginForm, RegistrationFrom, EditUserProfileForm



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
    """Home page"""
    return render_template('index.html')

@app.route('/user/<int:user_id>')
def user_profile(user_id):
    """Displays user profile and list of cars added"""
    user = User.query.get_or_404(user_id)
    cars = Car.query.filter_by(user_id=user.id).all()
    return render_template('user_profile.html', user=user, cars=cars)

@app.route('/user/<int:user_id>/update', methods=['GET', 'POST'])
def update_user_profile(user_id):
    """Updating user profile info"""
    if 'user_id' not in session or session['user_id'] != user_id:
        flash('You are not authorized to update this user info.', 'danger')
        return redirect(url_for('login'))
    
    user = User.query.get_or_404(user_id)
    form = EditUserProfileForm(obj=user)

    if form.validate_on_submit():
        user.name = form.name.data
        user.email = form.email.data
        user.profile_pic = form.profile_pic.data
        
        db.session.commit()
        flash('User info was updated successfully!', 'success')
        return redirect(url_for('user_profile', user_id=user.id))
    
    return render_template('update_user_profile.html', form=form, user=user)

    
@app.route('/get-car-info/', methods=['GET','POST'])
def get_car_info():
    """Gets car info from API and displays on the page"""
    vin = request.form['vin'].upper()
    
    car = Car.query.filter_by(vin=vin).first()

    if not car:
        fetch_data(vin)
        

    car_info = CarInfo.query.filter_by(car_id=car.id).first()
    return render_template('car_info.html', car_info=car_info)

@app.route('/show-car-info/<vin>')
def show_car_info(vin):
    """Displays car info when clicked on VIN"""
    car = Car.query.filter_by(vin=vin).first()
    car_info = CarInfo.query.filter_by(car_id=car.id).first()

    return render_template('show_car_info.html', car_info=car_info)


@app.route('/user/<int:user_id>/add', methods=['GET', 'POST'])
def add_car(user_id):
    """Add car to the user's profile"""
    if 'user_id' not in session or session['user_id'] != user_id:
        flash('You are not authorized to add a car for this user.', 'danger')
        return redirect(url_for('login'))

    vin = request.form['vin'].upper()
    car = Car.query.filter_by(vin=vin, user_id=user_id).first()

    if not car:
        fetch_data(vin, user_id)
        flash('Car added successfully!', 'success')
    else:
        flash('Car already exists.', 'info')
    return redirect(url_for('user_profile', user_id=user_id))

@app.route('/update-car-info/<vin>', methods=['POST'])
def update_car_info(vin):
    """Update car information for specific fields"""
    car = Car.query.filter_by(vin=vin).first()
    if not car:
        flash("Car not found.", "danger")
        return redirect(url_for('user_profile', user_id=session['user_id']))

    car_info = CarInfo.query.filter_by(car_id=car.id).first()
    if not car_info:
        flash("Car information not found.", "danger")
        return redirect(url_for('user_profile', user_id=session['user_id']))

    if 'year' in request.form and request.form['year']:
        car_info.year = request.form['year']
    if 'make' in request.form and request.form['make']:
        car_info.make = request.form['make']
    if 'model' in request.form and request.form['model']:
        car_info.model = request.form['model']
    if 'trim' in request.form and request.form['trim']:
        car_info.trim = request.form['trim']
    if 'top_speed' in request.form and request.form['top_speed']:
        car_info.top_speed = request.form['top_speed']
    if 'cylinders' in request.form and request.form['cylinders']:
        car_info.cylinders = request.form['cylinders']
    if 'horsepower' in request.form and request.form['horsepower']:
        car_info.horsepower = request.form['horsepower']
    if 'turbo' in request.form and request.form['turbo']:
        car_info.turbo = request.form['turbo']
    if 'engine_model' in request.form and request.form['engine_model']:
        car_info.engine_model = request.form['engine_model']
    if 'transmission_style' in request.form and request.form['transmission_style']:
        car_info.transmission_style = request.form['transmission_style']
    if 'drive_type' in request.form and request.form['drive_type']:
        car_info.drive_type = request.form['drive_type']

    db.session.commit()
    flash("Car information updated successfully.", "success")
    return redirect(url_for('show_car_info', vin=vin))

@app.route('/remove-car/<int:car_id>', methods=['POST'])
def remove_car(car_id):
    """Removes a car from the user's profile"""
    user_id = session['user_id']
    car = Car.query.get_or_404(car_id)

    if 'user_id' not in session or session['user_id'] != user_id:
        flash('You are not authorized to delete the car.', 'danger')
        return redirect(url_for('login'))
    
    db.session.delete(car)
    db.session.commit()

    flash('Car removed successfully!', 'success')
    return redirect(url_for('user_profile', user_id=user_id))
    


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
        session['user_id'] = new_user.id
        session['user_name'] = new_user.name
        return redirect(url_for('index', user_id=new_user.id))

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
            session['user_id'] = user.id
            session['user_name'] = user.name
            flash('Logged In Successfully', 'success')
            return redirect(url_for('user_profile', user_id=user.id))
        else:
            form.email.errors = ['Invalid email/password.']

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    """Logs out the user"""
    session.pop('user_id')
    session.pop('user_name')
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))