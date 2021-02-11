from flask import Blueprint, request, render_template, redirect, url_for, send_file
from flask_login import login_user, login_required, logout_user
from werkzeug.security import check_password_hash
from io import BytesIO
from time import sleep
from . import db
from .models import User
from .model_weights import Controller, base_dir

main = Blueprint('main', __name__)
model = Controller()
tracks_dict = model.get_labels()


MAX_TRACK_COUNT = 10


@main.route("/", methods=["GET", "POST"])
@login_required
def main_page():
	if request.method == "POST":
		file = request.files["file"]
		if not file:
			return "Выберите файл"


		data = BytesIO()
		file.save(data)

		result = model.predict(BytesIO(data.getvalue()))
		print(result)
		
		local_tracks = []
		for _, row in zip(range(MAX_TRACK_COUNT), result):
			label_value, value = row
			label_data = tracks_dict[label_value]

			local_tracks.append({
				# "title": label_value,
				"title": label_data["title"],
				"author": label_data["author"],
				"yandex_link": "https://music.yandex.ru/track/{}".format(label_data["track_id"]),
				"percent": str(round(value * 100, 2)) + "%",
				"link": url_for("main.download", _external=True, uid=label_value)
			})

		return render_template("index.html", tracks=enumerate(local_tracks, start=1))
	return render_template("index.html")


@main.route("/download/<uid>")
def download(uid):
	if tracks_dict.get(uid):
		filename = uid + ".mp3"
		return send_file(base_dir / "Dataset/YandexTracks" / filename, attachment_filename=tracks_dict[uid]["title"] + ".mp3", as_attachment=True)

	return "error"


@main.route("/logout")
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


