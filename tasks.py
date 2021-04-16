from flask import Flask, request
from flask_celery_conf import make_celery
from flask_sqlalchemy import SQLAlchemy
import os


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





if __name__ == '__main__':
    app.run(debug=True, port=9090)

