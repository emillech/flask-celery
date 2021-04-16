from flask import Flask, request, jsonify
from flask_celery_conf import make_celery
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
import os
import requests
import json


app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'amqp://localhost//'
app.config['CELERY_RESULT_BACKEND'] = 'db+sqlite:///db.sqlite3'

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

celery = make_celery(app)

db = SQLAlchemy(app)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)

    def __init__(self, name):
        self.name = name


class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)

    def __init__(self, name):
        self.name = name


@app.route('/index', methods=['GET'])
def index():
    req = requests.get('https://vpic.nhtsa.dot.gov/api/vehicles/getallmakes?format=json')
    data = json.loads(req.content)

    return jsonify(data['Results'][2]["Make_Name"])


@app.route('/get_name/<car_name>', methods=['GET', 'POST'])
def fetching_name(car_name):
    return get_name(car_name)


@app.route('/insert_data', methods=['POST'])
def insert():
    return insert_product()


@app.route('/process/<name>', methods=['GET', 'POST'])
def process(name):
    reverse.delay(name)
    return 'I sent request'


@celery.task(name='tasks.add')
def insert_product():
    name = request.json['name']

    result = Product(name=name)
    db.session.add(result)
    db.session.commit()
    return 'done'


@celery.task(name='tasks.reverse')
def reverse(text):
    return text[::-1]


@celery.task(name='tasks.get_name')
def get_name(car_name):
    # car_name = request.json['car_name']
    result = Car(name=car_name)
    req = requests.get('https://vpic.nhtsa.dot.gov/api/vehicles/getallmakes?format=json')
    data = json.loads(req.content)
    for i in range(500):

        search = data['Results'][i]["Make_Name"]

        if car_name in search:
            try:
                db.session.add(result)
                db.session.commit()
                return 'done'
            except exc.IntegrityError:
                return 'duplicate'
    return f'no name {car_name}'


if __name__ == '__main__':
    app.run(debug=True, port=9080)

