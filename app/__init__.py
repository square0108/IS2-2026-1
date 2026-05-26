## Template de flask docs
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy # usar para cargar DB


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        # SECRET_KEY='dev',
        # DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # Para cada ruta de cada tipo de usuario será necesario registrar un blueprint
    from app.auth.routes import auth
    app.register_blueprint(auth)

    from app.students.routes import students
    app.register_blueprint(students)
    
    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    return app