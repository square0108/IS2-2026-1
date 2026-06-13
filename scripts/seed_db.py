import sys
import os
from datetime import datetime, timedelta

# Añadimos la raíz para reconocer el módulo 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from app.db_model import db, Usuario, Curso, Estudiante, Incidente, Caso

app = create_app()

with app.app_context():
    # Borramos y creamos de nuevo la estructura
    db.drop_all()
    db.create_all()

    # ==========================
    # 1. CREACIÓN DE USUARIOS
    # ==========================
    # Reportadores (Profesores/Inspectores)
    u1 = Usuario(username="luis.profesor", nombre_completo="Luis Profesor", es_reportador=True)
    u1.set_password("123")
    u2 = Usuario(username="carmen.inspectora", nombre_completo="Carmen Inspectora", es_reportador=True)
    u2.set_password("123")

    # Encargados de Convivencia
    u3 = Usuario(username="ana.directora", nombre_completo="Ana Directora", es_encargado=True)
    u3.set_password("1234")
    u4 = Usuario(username="roberto.convivencia", nombre_completo="Roberto Convivencia", es_encargado=True)
    u4.set_password("1234")

    # ==========================
    # 2. CREACIÓN DE CURSOS Y ALUMNOS
    # ==========================
    c1 = Curso(nombre="1 Medio A")
    c2 = Curso(nombre="2 Medio B")
    c3 = Curso(nombre="3 Medio A")

    estudiantes = [
        Estudiante(rut="11111111-1", nombre_completo="Juan Pérez", curso=c1),
        Estudiante(rut="22222222-2", nombre_completo="Pedro Gómez", curso=c1),
        Estudiante(rut="33333333-3", nombre_completo="Diego López", curso=c1),
        Estudiante(rut="44444444-4", nombre_completo="María Soto", curso=c2),
        Estudiante(rut="55555555-5", nombre_completo="Sofía Riquelme", curso=c2),
        Estudiante(rut="66666666-6", nombre_completo="Joaquín Silva", curso=c3),
        Estudiante(rut="77777777-7", nombre_completo="Camila Castro", curso=c3),
        Estudiante(rut="88888888-8", nombre_completo="Benjamín Rojas", curso=c3),
        Estudiante(rut="88888838-2", nombre_completo="Benjamín Rodriguez", curso=c3),
        Estudiante(rut="99999991-1", nombre_completo="Valentina Fuentes", curso=c3),
        Estudiante(rut="88888888-6", nombre_completo="Benjamín Rojas", curso=c3),
        Estudiante(rut="99999999-5", nombre_completo="Valentina Fuente", curso=c3),
        Estudiante(rut="88888888-3", nombre_completo="Benjamín Amarillo", curso=c3),
        Estudiante(rut="88888888-2", nombre_completo="Eduardo Parra", curso=c1),
        Estudiante(rut="88888888-1", nombre_completo="Eduardo Roldan", curso=c3),
        Estudiante(rut="88284888-8", nombre_completo="Benjamín Vega", curso=c3)
    ]

    db.session.add_all([u1, u2, u3, u4, c1, c2, c3] + estudiantes)
    db.session.commit() # Guardamos para que obtengan sus IDs

    # ==========================
    # 3. CREACIÓN DE INCIDENTES
    # ==========================
    # Incidente 1: Físico, reportado por Luis (1 Medio A)
    inc1 = Incidente(
        descripcion="Juan Pérez empujó a Pedro Gómez durante el recreo.",
        respuesta_inmediata="Se separó a los estudiantes y se dialogó con ambos.",
        categoria="Físico",
        estudiantes=[estudiantes[0], estudiantes[1]],
        creador=u1,
        fecha_adicion=datetime.utcnow() - timedelta(days=5)
    )

    # Incidente 2: Verbal, reportado por Carmen (2 Medio B)
    inc2 = Incidente(
        descripcion="Discusión fuerte en sala de clases entre María y Sofía por un trabajo grupal.",
        respuesta_inmediata="Se calmó la situación y se asignó mediación.",
        categoria="Verbal",
        estudiantes=[estudiantes[3], estudiantes[4]],
        creador=u2,
        fecha_adicion=datetime.utcnow() - timedelta(days=3)
    )

    # Incidente 3: Cyberbullying, reportado por Ana Directora (1 Medio A)
    inc3 = Incidente(
        descripcion="Diego envió mensajes ofensivos a Juan a través de redes sociales.",
        respuesta_inmediata="Se citó a los apoderados de ambos alumnos.",
        categoria="Ciberacoso",
        estudiantes=[estudiantes[0], estudiantes[2]],
        creador=u3,
        fecha_adicion=datetime.utcnow() - timedelta(days=2)
    )

    # Incidente 4: Físico, reportado por Roberto (3 Medio A)
    inc4 = Incidente(
        descripcion="Camila y Benjamín pelearon en la entrada del colegio.",
        respuesta_inmediata="Intervención inmediata y citación a inspectoría.",
        categoria="Físico",
        estudiantes=[estudiantes[6], estudiantes[7]],
        creador=u4,
        fecha_adicion=datetime.utcnow() - timedelta(days=1)
    )

    db.session.add_all([inc1, inc2, inc3, inc4])
    db.session.commit()

    # ==========================
    # 4. CREACIÓN DE CASOS
    # ==========================
    # Caso 1: Gestionado por Ana Directora (Involucra a Juan, Pedro y Diego de 1MA)
    caso1 = Caso(
        nombre="Conflictos reiterados 1 Medio A",
        encargado=u3,
        estado="ABIERTO",
        fecha_creacion=datetime.utcnow() - timedelta(days=1)
    )
    # Vinculamos incidentes 1 y 3 a este caso
    caso1.evidencias.extend([inc1, inc3])

    # Caso 2: Gestionado por Roberto Convivencia (Involucra a María y Sofía)
    caso2 = Caso(
        nombre="Disputa académica 2 Medio B",
        encargado=u4,
        estado="RESUELTO",
        fecha_creacion=datetime.utcnow() - timedelta(days=2)
    )
    # Vinculamos incidente 2
    caso2.evidencias.append(inc2)

    db.session.add_all([caso1, caso2])
    db.session.commit()

    print("Base de datos poblada exitosamente.")