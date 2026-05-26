import sys
import os

# añadimos la raiz para reconocer modulo 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from app.db_model import db, Usuario, Curso, Estudiante, Incidente

app = create_app()

with app.app_context():
    # borramos
    db.drop_all()
    db.create_all()

    # usuarios
    u1 = Usuario(username="luis.profesor", nombre_completo="Luis Profesor", es_reportador=True)
    u2 = Usuario(username="ana.directora", nombre_completo="Ana Directora", es_encargado=True)
    
    # cursos
    c1 = Curso(nombre="1 Medio A")
    c2 = Curso(nombre="2 Medio B")

    # estudiantes
    e1 = Estudiante(rut="11111111-1", nombre_completo="Juan Pérez", curso=c1)
    e2 = Estudiante(rut="22222222-2", nombre_completo="Pedro Gómez", curso=c1)
    e3 = Estudiante(rut="33333333-3", nombre_completo="Diego López", curso=c2)

    # incidente
    incidente_prueba = Incidente(
        descripcion="Juan Pérez fue visto tirando papeles en clase.",
        respuesta_inmediata="Se indicó al alumno que fuera a Inspectoría.",
        estudiante=e1,
        creador=u1
    )

    # añadimos a la sesion y guardamos
    db.session.add_all([u1, u2, c1, c2, e1, e2, e3, incidente_prueba])
    db.session.commit()

    print("Base de datos poblada exitosamente.")