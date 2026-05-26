from flask import Blueprint, render_template, request, flash, redirect, url_for, session, redirect
from app.auth.login_required import login_required

reportador = Blueprint('reportador', __name__)
from app.db_model import Estudiante, Curso

CONST_ENTRADAS_POR_PAGINA = 25

@reportador.route('/')
@login_required("reportador")
def home():
  return render_template('reporter_home.html')

# - Modificar search_students.html: determinar cómo se pasará la lista de estudiantes a template
# - ¿Cuántos estudiantes se desplegarán? ¿Cómo implementar "páginas" de estudiantes"?
# - ¿Cómo implementar búsqueda/filtros desde interfaz, por nombre de estudiante y por curso?
# - ¿Cómo implementar selección de estudiantes para registrar incidente?

@reportador.route('/reportarIncidente', methods=["GET","POST"])
@login_required("reportador")
def nuevoReporte():
  if request.method == "GET":
    # Para desplegar la lista de estudiantes y los cursos para filtrar
    query_EstudianteCurso = Estudiante.query.join(Curso)
    query_cursos = Curso.query.order_by(Curso.nombre.asc()).all() 

    query_EstudianteCurso = query_EstudianteCurso.order_by(Estudiante.nombre_completo.asc(), Curso.nombre.asc()) # ordenamiento primero por curso y luego alfabetico
    # query_EstudianteCurso_paginada = query_EstudianteCurso.paginate(page=1, per_page=CONST_ENTRADAS_POR_PAGINA, error_out=False) # cambiar esto después para múltiples páginas

    return render_template('components/search_students.html',
                           EstudianteCurso_todos=query_EstudianteCurso,
                           Cursos=query_cursos
                           ) # TODO: cambiar para que muestre entradas por páginas
  elif request.method == "POST":
    """
    El POST envia un diccionario con los valores: [
      ('id_estudiantes_involucrados', <id>),
      ('id_estudiantes_involucrados', <id2>),
      ( ... ),
      ('categoria_incidente', <fisico/verbal>),
      ('descripcion', <string>),
      ('respuesta_inmediata', <string>)]
      Es decir, si desde Flask quieren acceder a los id's de todos los involucrados enviados, hagan lista = request.form.getlist('id_estudiantes_involucrados').
    """
    # debuggin'
    print(request.form.get('categoria_incidente'))
    print(request.form.get('descripcion'))
    print(request.form.get('respuesta_inmediata'))
    ids_estudiantes = request.form.getlist('id_estudiantes_involucrados')
    for id in ids_estudiantes:
      print(id)

    # TODO: agregar incidente a la BD

    flash("Reporte registrado exitosamente", "success")
    return redirect(url_for('reportador.nuevoReporte'))