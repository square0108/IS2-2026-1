from flask import Blueprint, render_template, request, flash, redirect, url_for, session, redirect
from app.auth.login_required import login_required
from app.queries import listar_consultas, ejecutar_consulta

from app.db_model import db, Estudiante, Curso, Incidente

reportador = Blueprint('reportador', __name__)

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
  ## --- GET --- #
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
  
  ## --- POST --- #
  elif request.method == "POST":
      # Recuperar datos del formulario
      categoria = request.form.get('categoria_incidente')
      descripcion = request.form.get('descripcion')
      respuesta_inmediata = request.form.get('respuesta_inmediata')
      ids_estudiantes = request.form.getlist('id_estudiantes_involucrados')

      # CA4: Validación para evitar reportes incompletos o con menos de 2 estudiantes
      if not categoria or not descripcion or len(ids_estudiantes) < 1:
          flash("Error: Debe ingresar una descripción, una categoría y seleccionar al menos a un estudiante.", "danger")
          return redirect(url_for('reportador.nuevoReporte'))

      # Obtener los objetos Estudiante desde la base de datos usando el operador in_
      estudiantes_involucrados = Estudiante.query.filter(Estudiante.id.in_(ids_estudiantes)).all()

      # Crear la instancia del incidente
      nuevo_incidente = Incidente(
          descripcion=descripcion,
          respuesta_inmediata=respuesta_inmediata,
          categoria=categoria,
          estudiantes=estudiantes_involucrados,
          creador_id=session.get('user_id')  # El creador es el usuario logueado actualmente
      )

      try:
          # Añadir y guardar en la base de datos
          db.session.add(nuevo_incidente)
          db.session.commit()
          flash("Reporte registrado exitosamente", "success")
      except Exception as e:
          db.session.rollback() # Deshacer cambios si ocurre un error
          flash("Ocurrió un error de servidor al intentar registrar el reporte.", "danger")
          print(f"Error al guardar el incidente: {e}") # Para visibilidad en tu terminal

      return redirect(url_for('reportador.nuevoReporte'))
