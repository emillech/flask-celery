from flask import Flask
from flask_celery_conf import make_celery

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'amqb://localhost//'
app.config['CELERY_RESULT_BACKEND'] = 'db+sqlite:///db.sqlite3'

celery = make_celery(app)

@app.route('/process/<name>')
def process(name):
    return name


if __name__ == '__main__':
    app.run(debug=True)

