import sqlite3
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
import sys
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.secret_key = 'random stuff'
db = SQLAlchemy(app)

appid = '08db5953b42be229b4a04c7d9471f91e'
units = 'metric'


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return f"City(id='{self.id}', name='{self.name}')"


con = sqlite3.connect('weather.db')
cursor = con.cursor()
db.create_all()


@app.route('/')
def index():
    weather_info_list = []
    for city in City.query.all():
        response = get_response(city.name).json()
        state = response['weather'][0]['main']
        temp = response['main']['temp']
        city_name = city.name
        back_image = determine_time(int(response['timezone']))
        id = city.id
        weather_info = {'state': state,
                        'temp': temp,
                        'city_name': city_name,
                        'back_image': back_image,
                        'id': id}
        weather_info_list.append(weather_info)
    return render_template('index.html', weathers=weather_info_list)


@app.route('/', methods=['POST'])
def add_city():
    city_name = request.form.get('city_name').upper()
    if not get_response(city_name):
        flash("The city doesn't exist!")
    elif City.query.filter_by(name=city_name).first():
        flash("The city has already been added to the list!")
    else:
        city = City(name=city_name)
        db.session.add(city)
        db.session.commit()
    return redirect('/')


@app.route('/delete/<city_id>', methods=['POST'])
def delete_city(city_id):
    city = City.query.filter_by(id=city_id).first()
    db.session.delete(city)
    print("something")
    db.session.commit()
    return redirect('/')


def get_response(city_name):
    params = {'q': city_name, 'appid': appid, 'units': units}
    api_call = f'http://api.openweathermap.org/data/2.5/weather'
    return requests.get(api_call, params=params)


def determine_time(seconds):
    utc = datetime.utcnow()
    hour = (utc + timedelta(seconds=seconds)).time().hour
    back_image = 'day' if 18 > hour > 12 else 'night' \
        if 6 > hour else 'evening-morning'
    return back_image


# don't change the following way to run flask:
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
