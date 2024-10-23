# app/__init__.py
# connect secret_keys from config with instances in extensions 

from flask import Flask
from .extensions import db, jwt, cors, migrate
from .config import Config
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Intiaize extensions 
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    migrate.init_app(app, db)

    print(app.config['SQLALCHEMY_DATABASE_URI'])

    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app