from flask import Blueprint, render_template, session, request, flash, redirect, url_for
from app.auth.login_required import login_required
from app.db_model import db, Estudiante, Curso, Incidente

manager = Blueprint('encargado_de_convivencia', __name__)

@manager.route('/')
@login_required("encargado_de_convivencia")
def home():
    return render_template('manager_home.html')

@manager.route('/reportarIncidente', methods=["GET", "POST"])
@login_required("encargado_de_convivencia")
def nuevoReporte():
    if request.method == "GET":
        # Despliegue de listas
        query_EstudianteCurso = Estudiante.query.join(Curso).order_by(Estudiante.nombre_completo.asc(), Curso.nombre.asc())
        query_cursos = Curso.query.order_by(Curso.nombre.asc()).all() 

        return render_template('components/search_students.html',
                               EstudianteCurso_todos=query_EstudianteCurso,
                               Cursos=query_cursos)
                               
    elif request.method == "POST":
        categoria = request.form.get('categoria_incidente')
        descripcion = request.form.get('descripcion')
        respuesta_inmediata = request.form.get('respuesta_inmediata')
        ids_estudiantes = request.form.getlist('id_estudiantes_involucrados')

        # Validación
        if not categoria or not descripcion or len(ids_estudiantes) < 1:
            flash("Error: Debe ingresar una descripción, una categoría y seleccionar al menos a un estudiante.", "danger")
            return redirect(url_for('encargado_de_convivencia.nuevoReporte'))

        estudiantes_involucrados = Estudiante.query.filter(Estudiante.id.in_(ids_estudiantes)).all()

        # Al registrar, el creador será el encargado que inició sesión
        nuevo_incidente = Incidente(
            descripcion=descripcion,
            respuesta_inmediata=respuesta_inmediata,
            categoria=categoria,
            estudiantes=estudiantes_involucrados,
            creador_id=session.get('user_id')  
        )

        try:
            db.session.add(nuevo_incidente)
            db.session.commit()
            flash("Reporte registrado exitosamente", "success")
        except Exception as e:
            db.session.rollback() 
            flash("Ocurrió un error de servidor al intentar registrar el reporte.", "danger")
            print(f"Error al guardar el incidente: {e}") 

        return redirect(url_for('encargado_de_convivencia.nuevoReporte'))