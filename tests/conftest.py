import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import create_app
from app.db_model import db, Usuario, Curso, Estudiante

@pytest.fixture
def app():
    # Creamos la aplicación forzando la configuración de pruebas
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'test_secret'
    })
    return app

@pytest.fixture
def client(app):
    # Cliente para hacer peticiones HTTP en los tests
    return app.test_client()

@pytest.fixture
def init_database(app):
    # Prepara la base de datos de prueba antes de cada test
    with app.app_context():
        db.create_all()

        # Inyectamos datos mínimos necesarios para que las vistas no fallen
        u_rep = Usuario(username="test.reportador", nombre_completo="Test Reportador", es_reportador=True)
        u_rep.set_password("123")
        
        u_man = Usuario(username="test.manager", nombre_completo="Test Manager", es_encargado=True)
        u_man.set_password("123")

        c1 = Curso(nombre="1 Medio A")
        e1 = Estudiante(rut="111-1", nombre_completo="Alumno 1", curso=c1)
        e2 = Estudiante(rut="222-2", nombre_completo="Alumno 2", curso=c1)

        db.session.add_all([u_rep, u_man, c1, e1, e2])
        db.session.commit()

        yield db  # Aquí se ejecuta el test correspondiente

        # Limpiamos la base de datos al terminar el test
        db.session.remove()
        db.drop_all()

# Fixtures para simular sesiones ya iniciadas y ahorrar código
@pytest.fixture
def auth_reportador(client):
    with client.session_transaction() as session:
        session["user_id"] = 1 # ID de test.reportador
        session["user_type"] = "reportador"
        session["user_name"] = "Test Reportador"

@pytest.fixture
def auth_manager(client):
    with client.session_transaction() as session:
        session["user_id"] = 2 # ID de test.manager
        session["user_type"] = "encargado_de_convivencia"
        session["user_name"] = "Test Manager"