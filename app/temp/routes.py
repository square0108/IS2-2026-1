from flask import Blueprint, jsonify
from app.db_model import db, Usuario, Estudiante

temp = Blueprint('temp', __name__)

@temp.route('/test-db', methods=['GET', 'POST'])
def test_db():
    usuarios = Usuario.query.all()
    estudiantes = Estudiante.query.all()
    return jsonify({
        "status": "Conexión exitosa",
        "usuarios_registrados": [u.nombre_completo for u in usuarios],
        "estudiantes_registrados": [e.nombre_completo for e in estudiantes]
    })