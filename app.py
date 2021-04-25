import hashlib
import os
import json
import copy
import random
import time
from helpers import *
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from flask import Flask, render_template, redirect, url_for, request, flash, send_file, send_from_directory
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=ROOT_DIR + "/static/")
app.config["SECRET_KEY"] = "9OLWxND4o83j4K4iuopO"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db = SQLAlchemy()
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

authors = [{'name': 'Mahesh', 'github': 'https://github.com/MaheshBharadwaj'},
           {'name': 'Mahesh', 'github': 'https://github.com/MaheshBharadwaj'}, {'name': 'Mahesh', 'github': 'https://github.com/MaheshBharadwaj'}]


def check_password(user_password, password):
    return user_password == password


class User(UserMixin, db.Model):
    # primary keys are required by SQLAlchemy
    id = db.Column(db.String(20), primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(150))
    name = db.Column(db.String(100))

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


db.create_all(app=app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


@app.route("/", methods=["GET"])
def index():

    if request.method == "GET":
        return render_template(
            "index.html", page_title="SSN MUN 2021", authors=authors
        )


@app.route("/sign-up", methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html", popup=False)

    uname = request.form.get("uname")
    email = request.form.get("email")
    password = request.form.get("pwd1")
    print('Email: ', email)
    user_check = User.query.filter_by(email=email).first()
    print('user_check: ', user_check)
    if user_check is not None:
        return render_template("register.html", popup=True)

    user = User(id=generate_password_hash(email)
                [34:55], email=email, name=uname)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return redirect(url_for("login"))


@app.route("/login")
def login():
    return render_template("login.html", popup_email=False, popup_password=False)


@app.route("/login", methods=["POST"])
def login_post():
    email = request.form.get("email")
    password = request.form.get("password")
    print("password: ", password)
    remember = True  # if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()
    # check if user actually exists
    # take the user supplied password, hash it, and compare it to the hashed password in database
    if user is None:
        return render_template("login.html", popup_email=True, popup_password=False)
    if user.check_password(password) == False:
        return render_template("login.html", popup_email=False, popup_password=True)

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    if user.name == 'admin':
        return redirect(url_for("admin"))

    return redirect(url_for("index"))


@app.route("/admin")
@login_required
def admin():

    if current_user.name == 'admin':
        return render_template("admin.html")
    print(current_user.name)

    return render_template("403.html", name=current_user.name), 403


@app.route("/admin-logout")
@login_required
def admin_logout():

    if current_user.name == 'admin':
        logout_user()
        return redirect(url_for('login'))

    return render_template("403.html", name=current_user.name), 403


@app.route("/add-route", methods=['GET', 'POST'])
@login_required
def add_route():
    if current_user.name == 'admin':
        if request.method == 'GET':
            return render_template("add_route.html", page_title="Add Route Page", authors=authors)
        else:
            add_route_to_db(request=request)
            return render_template("add_route.html", page_title="Add Route Page", authors=authors, add_route_success=True)
    else:
        return render_template("403.html"), 403


@app.route("/add-flight", methods=['GET', 'POST'])
@login_required
def add_flight():
    if current_user.name == 'admin':
        if request.method == 'GET':
            return render_template("add_flight.html", page_title="Add Flight", authors=authors, routes_array=get_all_routes())
        else:
            add_flight_to_db(request=request)
            return render_template("add_flight.html", page_title="Add Flight", authors=authors, routes_array=get_all_routes(),
                                   add_flight_success=True)
    else:
        return render_template("403.html"), 403


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
