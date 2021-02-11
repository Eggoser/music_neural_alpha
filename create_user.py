from werkzeug.security import generate_password_hash
from manage import app as current_app
from app import db
from app.models import User


LOGIN = "hello"
PASSWORD = "world"


with current_app.app_context() as app:
	try:
		User.query.delete()
		db.session.drop_all()
	except:
		pass
	db.create_all()

	new_user = User(login=LOGIN, password=generate_password_hash(PASSWORD, method='sha256'))

	db.session.add(new_user)
	db.session.commit()
