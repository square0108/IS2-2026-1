## Template de flask docs
import os, datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy # usar para cargar DB
from app.db_model import db
from app.utils import datetime_sin_miliseg


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='dev',
        # DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.instance_path, 'flaskr.sqlite'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # Inicializamos la base de datos con la app
    db.init_app(app)
    # Creamos las tablas si no existen
    with app.app_context():
        db.create_all()

    # Para cada ruta de cada tipo de usuario será necesario registrar un blueprint
    from app.auth.routes import auth
    app.register_blueprint(auth)

    from app.temp.routes import temp    # rutas de prueba
    app.register_blueprint(temp)

    from app.users.reportador.routes import reportador
    app.register_blueprint(reportador, url_prefix='/reportador')

    from app.users.encargado_de_convivencia.routes import encargado
    app.register_blueprint(encargado, url_prefix='/encargado_de_convivencia')

    # from app.users.orientador.routes import orientador
    # app.register_blueprint(orientador, url_prefix='/orientador')

    # from app.students.routes import students
    # app.register_blueprint(students)

    # Paso de funciones utilidades
    app.jinja_env.filters['datetime_sin_miliseg'] = datetime_sin_miliseg

    return app