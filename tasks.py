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


class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)

    def __init__(self, name):
        self.name = name


@app.route('/index', methods=['GET'])
def index():
    req = requests.get('https://vpic.nhtsa.dot.gov/api/vehicles/getallmakes?format=json')
    data = json.loads(req.content)
    return jsonify(data['Results'])


@app.route('/get_name', methods=['GET'])
def fetching_name():
    brand = request.args.get("brand")
    get_name.delay(brand.upper())
    return 'done'


@celery.task(name='tasks.get_name')
def get_name(brand):
    result = Car(name=brand)
    req = requests.get('https://vpic.nhtsa.dot.gov/api/vehicles/getallmakes?format=json')
    data = json.loads(req.content)
    for i in range(len(data['Results'])):
        search = data['Results'][i]["Make_Name"]
        if brand == search:
            try:
                db.session.add(result)
                db.session.commit()
                return f'added {brand}'
            except exc.IntegrityError:
                return f'duplicate {brand}'
    return f'no name {brand}'


if __name__ == '__main__':
    app.run(debug=True, port=8080)

