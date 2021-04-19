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
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))


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


@app.route("/test")
def test():
    return render_template("403.html"), 403


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login_post():
    regid = request.form.get("regid")
    password = request.form.get("password")
    remember = True  # if request.form.get('remember') else False
    print("regid: %s\tpass: %s" % (regid, password))
    user = User.query.filter_by(name=regid).first()
    print('User:', user)
    # check if user actually exists
    # take the user supplied password, hash it, and compare it to the hashed password in database
    if not user or not check_password(user.password, password):
        flash("Please check your login details and try again.")
        print("Please check your login details and try again.")

        # print('incorrect pass actual pass: ', user.password)
        # if user doesn't exist or password is wrong, reload the page
        return redirect(url_for("login"))

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
            return render_template("add_route.html", authors=authors)
        else:
            add_route_to_db(request=request)
            return redirect(url_for("add_route"))
    else:
        return render_template("403.html"), 403


@app.route("/add-flight", methods=['GET', 'POST'])
@login_required
def add_flight():
    if current_user.name == 'admin':
        if request.method == 'GET':
            return render_template("add_flight.html", authors=authors, routes_array=get_all_routes())
        else:
            add_flight_to_db(request=request)
            return redirect(url_for("add_flight"))
    else:
        return render_template("403.html"), 403


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
