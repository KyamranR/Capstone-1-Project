import os
from flask import Flask, render_template, request, flash, redirect, session, url_for
from models import db, connect_db, User, Car, CarInfo, fetch_data
import requests



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
    car = Car.query.filter_by(vin=vin).first()

    if not car:
        fetch_data(vin)
        car = Car.query.filter_by(vin=vin).first()

    car_info = CarInfo.query.filter_by(car_id=car.id).first()
    return render_template('car_info.html', car_info=car_info)
    