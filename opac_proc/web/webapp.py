# coding: utf-8
from flask import Flask
from flask import render_template, flash  # redirect,
from flask.ext.mongoengine import MongoEngine
from flask.ext.wtf import Form
from wtforms import validators, StringField, TextAreaField
import rq_dashboard

app = Flask(
    __name__,
    static_url_path='/static',
    static_folder='static',
    instance_relative_config=False)
app.config.from_pyfile('config.py')
app.config.from_object(rq_dashboard.default_settings)
db = MongoEngine(app)
app.register_blueprint(rq_dashboard.blueprint, url_prefix='/dashboard')


@app.route('/', methods=('GET', 'POST'))
def home():
    context = {}
    return render_template("home.html", **context)


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8001,
        debug=True)
