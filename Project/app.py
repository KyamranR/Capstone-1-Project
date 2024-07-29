import os
from flask import Flask, render_template, request, flash, redirect, session, url_for
from models import db, connect_db, User, Car, CarInfo, fetch_car_data, save_car_data
from form import LoginForm, RegistrationForm, EditUserProfileForm, EditCarInfoForm



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

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register form for users"""

    form = RegistrationForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        profile_pic = form.profile_pic.data or User.profile_pic.default.arg
        password = form.password.data

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('User already exists. Please choose different email.', 'error')
            return redirect('/register')

        new_user = User.register(name, email, profile_pic, password)

        try:
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id
            session['user_name'] = new_user.name
            flash('Registered successfully!', 'success')
        except:
            db.session.rollback()
            flash('Error registering user. Please try again.', 'dager')

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

@app.route('/user/<int:user_id>')
def user_profile(user_id):
    """Displays user profile and list of cars added"""
    if 'user_id' not in session or session['user_id'] != user_id:
        flash('You are not authorized to view this user info.', 'danger')
        return redirect(url_for('index'))

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
        if form.profile_pic.data:
            user.profile_pic = form.profile_pic.data
        else:
            user.profile_pic = User.profile_pic.default.arg
        try:    
            db.session.commit()
            flash('User info was updated successfully!', 'success')
        except:
            db.session.rollback()
            flash('Error updating user info. Please try again.', 'danger')
            
        return redirect(url_for('user_profile', user_id=user.id))
    
    return render_template('update_user_profile.html', form=form, user=user)

    
@app.route('/get-car-info/', methods=['GET', 'POST'])
def get_car_info():
    """Gets car info from API and displays on the page"""
    vin = request.form.get('vin', '').upper()

    if not vin:
        flash('VIN is required.', 'danger')
        return redirect(url_for('index'))
    
    car = Car.query.filter_by(vin=vin).first()

    if not car:
        car_info = fetch_car_data(vin)

        if car_info:
            return render_template('car_info.html', car_info=car_info, vin=vin)
        else:
            flash('Car info could not be retrieved.', 'danger')
            return redirect(url_for('index'))
        

    car_info = CarInfo.query.filter_by(car_id=car.id).first()
    return render_template('car_info.html', car_info=car_info, vin=vin)


@app.route('/show-car-info/<vin>', methods=['GET', 'POST'])
def show_car_info(vin):
    """Displays car info when clicked on VIN"""
    user_id = session.get('user_id')
    if not user_id:
        flash('User not logged in.', 'danger')
        return redirect(url_for('login'))
    
    car = Car.query.filter_by(vin=vin, user_id=user_id).first()
    if not car:
        flash('Car not found.', 'danger')
        return redirect(url_for('user_profile', user_id=user_id))
    
    car_info = CarInfo.query.filter_by(car_id=car.id).first()
    if not car_info:
        flash('Car info could not be found.', 'danger')
        return redirect(url_for('user_profile', user_id=user_id))

    return render_template('show_car_info.html', car_info=car_info, vin=vin)


@app.route('/update-car-info/<vin>', methods=['GET', 'POST'])
def update_car_info(vin):
    """Update car information for specific fields"""
    user_id = session.get('user_id')
    if not user_id:
        flash('User not logged in.', 'danger')
        return redirect(url_for('login'))
    
    car = Car.query.filter_by(vin=vin, user_id=user_id).first()
    if not car:
        flash("Car not found.", "danger")
        return redirect(url_for('user_profile', user_id=user_id))

    car_info = CarInfo.query.filter_by(car_id=car.id).first()
    if not car_info:
        flash("Car information not found.", "danger")
        return redirect(url_for('user_profile', user_id=user_id))

    form = EditCarInfoForm(obj=car_info)
    
    if request.method == 'GET':
        if car_info.turbo is None:
            form.turbo.data = 'False'
        elif car_info.turbo == 'True':
            form.turbo.data = 'True'
        else:
            form.turbo.data = 'False'

    if form.validate_on_submit():
        car_info.year = form.year.data or car_info.year
        car_info.make = form.make.data or car_info.make
        car_info.model = form.model.data or car_info.model
        car_info.trim = form.trim.data or car_info.trim
        car_info.top_speed = form.top_speed.data or car_info.top_speed
        car_info.cylinders = form.cylinders.data or car_info.cylinders
        car_info.horsepower = form.horsepower.data or car_info.horsepower
        
        if form.turbo.data == 'True':
            car_info.turbo = 'True'
        elif form.turbo.data == 'False':
            car_info.turbo = 'False'
        else:
            car_info.turbo = None

        car_info.engine_model = form.engine_model.data or car_info.engine_model
        car_info.transmission_style = form.transmission_style.data or car_info.transmission_style
        car_info.drive_type = form.drive_type.data or car_info.drive_type
    
        try:
            db.session.commit()
            flash("Car information updated successfully.", "success")
        except:
            db.session.rollback()
            flash('Error updating car information. Please try again.', 'danger')

        return redirect(url_for('show_car_info', vin=vin))
    
    return render_template('update_car_info.html', form=form, vin=vin)

@app.route('/user/<int:user_id>/add', methods=['POST'])
def add_car(user_id):
    if 'user_id' not in session or session['user_id'] != user_id:
        flash('You are not authorized to add a car for this user.', 'danger')
        return redirect(url_for('login'))

    vin = request.form.get('vin', '').upper()
    if not vin:
        flash('VIN is required.', 'danger')
        return redirect(url_for('user_profile', user_id=user_id))

    car = Car.query.filter_by(vin=vin, user_id=user_id).first()
    if not car:
        car_info = fetch_car_data(vin)
        if car_info:
            save_car_data(vin, user_id, car_info)
            flash('Car added successfully!', 'success')
        else:
            flash('Car info could not be retrieved.', 'danger')
    else:
        flash('Car already exists.', 'danger')

    return redirect(url_for('user_profile', user_id=user_id))

@app.route('/remove-car/<int:car_id>', methods=['POST'])
def remove_car(car_id):
    """Removes a car from the user's profile"""
    user_id = session['user_id']
    car = Car.query.get_or_404(car_id)

    if 'user_id' not in session or session['user_id'] != user_id:
        flash('You are not authorized to delete the car.', 'danger')
        return redirect(url_for('login'))
    
    try:
    
        db.session.delete(car)
        db.session.commit()
        flash('Car removed successfully!', 'success')

    except:
        db.session.rollback()
        flash('Error removing car. Please try again.', 'danger')
    return redirect(url_for('user_profile', user_id=user_id))
    




if __name__ == '__main__':
    app.run(debug=True)