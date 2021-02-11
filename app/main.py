from flask import Blueprint, request, render_template, redirect, url_for
from flask_login import login_user, login_required, logout_user
from werkzeug.security import check_password_hash
from . import db
from .models import User

main = Blueprint('main', __name__)

@main.route("/")
@login_required
def main_page():
	return "hello world"

@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("main.authentication"))


@main.route("/auth", methods=["GET", "POST"])
def authentication():
	if request.method == "POST":
		login = request.form["login"]
		password = request.form["password"]

		user = User.query.filter_by(login=login).first()

		if not user or not check_password_hash(user.password, password):
			return redirect(url_for("main.authentication"))

		login_user(user, remember=True)
		return redirect(url_for("main.main_page"))

	return render_template("auth.html")


