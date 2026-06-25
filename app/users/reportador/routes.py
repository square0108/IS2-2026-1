from flask import Blueprint, render_template, request, flash, redirect, url_for, session, redirect
from app.auth.login_required import login_required
from app.queries import listar_consultas, ejecutar_consulta
from app.db_model import Accion
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

      return render_template('shared_components/registrar_antecedente.html',
                             EstudianteCurso_todos=estudiantes,
                             Cursos=query_cursos,
                             pagination=pagination,
                             busqueda=busquedaNombreCurso,
                             curso=curso)
  
  ## --- POST --- #
  elif request.method == "POST":
      tipo_antecedente = request.form.get('tipoAntecedente')
      descripcion = request.form.get('descripcion')
      ids_estudiantes = request.form.getlist('id_estudiantes_involucrados')

      # Validación de Seguridad
      if tipo_antecedente != 'incidente':
          flash("No tiene permisos para registrar este tipo de antecedente.", "danger")
          return redirect(url_for('reportador.nuevoReporte'))

      # Validación Base
      if not descripcion or len(ids_estudiantes) < 1:
          flash("Error: Debe ingresar una descripción y seleccionar al menos a un estudiante.", "danger")
          return redirect(url_for('reportador.nuevoReporte'))

      categoria = request.form.get('categoria_incidente')
      respuesta_inmediata = request.form.get('respuesta_inmediata')

      if not categoria:
          flash("Error: Debe seleccionar una categoría para el incidente.", "danger")
          return redirect(url_for('reportador.nuevoReporte'))

      estudiantes_involucrados = Estudiante.query.filter(Estudiante.id.in_(ids_estudiantes)).all()

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
          flash("Incidente registrado exitosamente", "success")
      except Exception as e:
          db.session.rollback()
          flash("Ocurrió un error de servidor al intentar registrar el reporte.", "danger")
          print(f"Error al guardar el incidente: {e}")

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

@reportador.route('/misAcciones')
@login_required("reportador")
def misAcciones():

    acciones = (
        Accion.query
        .filter_by(asignado_id=session.get('user_id'))
        .order_by(Accion.fecha_emision.desc())
        .all()
    )

    return render_template(
        'shared_components/mis_acciones.html',
        acciones=acciones,
        detalle_endpoint='reportador.detalleAccion'
    )

@reportador.route('/accion/<int:accion_id>', methods=["GET", "POST"])
@login_required("reportador")
def detalleAccion(accion_id):

    accion = Accion.query.get_or_404(accion_id)

    if accion.asignado_id != session.get('user_id'):
        flash("No tienes permiso para acceder a esta acción.", "danger")
        return redirect(url_for('reportador.misAcciones'))

    if request.method == "POST":

        accion.resultado = request.form.get('resultado')
        accion.estado = "COMPLETADA"

        try:
            db.session.commit()
            flash("Acción completada exitosamente.", "success")
        except Exception as e:
            db.session.rollback()
            flash("Error al guardar la acción.", "danger")
            print(e)

        return redirect(
            url_for(
                'reportador.detalleAccion',
                accion_id=accion.id
            )
        )

    return render_template(
        'shared_components/detalle_accion.html',
        accion=accion,
        back_url=url_for('reportador.misAcciones')
    )