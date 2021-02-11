from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'sdfkjh2!3krhluadlsfj224olSLAS234JFIQOWELA59KSaIRLadsfSAFAOWUO0=(@$ahda349as'
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(os.path.dirname(os.path.dirname(__file__)), "db.sqlite3")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'main.authentication'
    login_manager.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
