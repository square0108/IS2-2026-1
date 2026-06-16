from flask import Blueprint, render_template, request, flash, redirect, url_for, session, redirect
from app.auth.login_required import login_required
from app.queries import listar_consultas, ejecutar_consulta

from app.db_model import db, Estudiante, Curso, Incidente

reportador = Blueprint('reportador', __name__)

CONST_ENTRADAS_POR_PAGINA = 25


@reportador.route('/')
@login_required("reportador")
def home():
  return render_template('reportador/reportador_home.html')


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
      query_cursos = Curso.query.order_by(Curso.nombre.asc()).all()

      busquedaNombreCurso = request.args.get('busqueda')
      curso = request.args.get('curso')
      page = request.args.get('page', 1, type=int)
      
      # Construir query con filtros
      query = Estudiante.query.join(Curso)
      
      if curso:
          query = query.filter(Curso.nombre == curso)
      
      if busquedaNombreCurso:
          like_q = f"%{busquedaNombreCurso}%"
          query = query.filter(Estudiante.nombre_completo.ilike(like_q))
      
      # Aplicar paginación: 10 estudiantes por página
      pagination = query.order_by(
          Estudiante.nombre_completo.asc(),
          Curso.nombre.asc()
      ).paginate(page=page, per_page=10, error_out=False)
      
      estudiantes = pagination.items

      return render_template('shared_components/reportar_incidente_lista.html',
                            EstudianteCurso_todos=estudiantes,
                            Cursos=query_cursos,
                            pagination=pagination,
                            busqueda=busquedaNombreCurso,
                            curso=curso)
  
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


@reportador.route('/misReportes')
@login_required("reportador")
def misReportes():
    # Identificar al usuario activo en la sesión
    usuario_actual = session.get('user_id')
    
    # Obtener número de página desde parámetros GET (por defecto 1)
    page = request.args.get('page', 1, type=int)
    
    # Consultar a la BD filtrando por el creador y ordenando por los más recientes primero
    # Usar paginación: 10 incidentes por página
    pagination = (
        Incidente.query
        .filter_by(creador_id=usuario_actual)
        .order_by(Incidente.fecha_adicion.desc())
        .paginate(page=page, per_page=10, error_out=False)
    )
    
    incidentes = pagination.items
    
    # Renderizar el nuevo template pasándole la lista de incidentes y la paginación
    return render_template('shared_components/mis_reportes.html', incidentes=incidentes, pagination=pagination)
