from flask import Blueprint, render_template, session, request, flash, redirect, url_for
from app.auth.login_required import login_required
from app.db_model import db, Estudiante, Curso, Incidente, Caso, Antecedente, Observacion
from app.queries import ejecutar_consulta

encargado = Blueprint('encargado_de_convivencia', __name__)

@encargado.route('/')
@login_required("encargado_de_convivencia")
def home():
    return render_template('encargado_de_convivencia/encargado_home.html')


@encargado.route('/reportarIncidente', methods=["GET", "POST"])
@login_required("encargado_de_convivencia")
def nuevoReporte():
    if request.method == "GET":
        # Despliegue de listas
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
                               
    elif request.method == "POST":
        tipo_antecedente = request.form.get('tipoAntecedente')
        descripcion = request.form.get('descripcion')
        ids_estudiantes = request.form.getlist('id_estudiantes_involucrados')

        # Validación de Seguridad
        if tipo_antecedente not in ['incidente', 'observacion']:
            flash("Tipo de registro no válido o sin permisos.", "danger")
            return redirect(url_for('encargado_de_convivencia.nuevoReporte'))

        # Validación Base
        if not descripcion or len(ids_estudiantes) < 1:
            flash("Error: Debe ingresar una descripción y seleccionar al menos a un estudiante.", "danger")
            return redirect(url_for('encargado_de_convivencia.nuevoReporte'))

        estudiantes_involucrados = Estudiante.query.filter(Estudiante.id.in_(ids_estudiantes)).all()
        nuevo_antecedente = None

        # Bifurcación
        if tipo_antecedente == 'incidente':
            categoria = request.form.get('categoria_incidente')
            respuesta_inmediata = request.form.get('respuesta_inmediata')
            
            if not categoria:
                flash("Error: Debe seleccionar una categoría para el incidente.", "danger")
                return redirect(url_for('encargado_de_convivencia.nuevoReporte'))
                
            nuevo_antecedente = Incidente(
                descripcion=descripcion,
                respuesta_inmediata=respuesta_inmediata,
                categoria=categoria,
                estudiantes=estudiantes_involucrados,
                creador_id=session.get('user_id')
            )
            
        elif tipo_antecedente == 'observacion':
            nuevo_antecedente = Observacion(
                descripcion=descripcion,
                estudiantes=estudiantes_involucrados,
                creador_id=session.get('user_id')
            )

        try:
            db.session.add(nuevo_antecedente)
            db.session.commit()
            flash("Registro guardado exitosamente", "success")
        except Exception as e:
            db.session.rollback()
            flash("Ocurrió un error al intentar registrar la información.", "danger")
            print(f"Error al guardar: {e}")

        return redirect(url_for('encargado_de_convivencia.nuevoReporte'))


@encargado.route('/explorarIncidentes', methods=["GET"])
@login_required("encargado_de_convivencia")
def explorarIncidentes():
    # Obtenemos el filtro por GET (si no existe, por defecto es 'todos')
    filtro = request.args.get('filtro', 'todos')
    
    # Obtener número de página desde parámetros GET (por defecto 1)
    page = request.args.get('page', 1, type=int)
    
    # Consultamos exclusivamente los Incidentes
    query = Incidente.query.order_by(Incidente.fecha_adicion.desc())
    
    # Aplicamos el filtro si el usuario quiere ver solo los suyos
    if filtro == 'mios':
        query = query.filter_by(creador_id=session.get('user_id'))
    
    # Usar paginación: 10 incidentes por página
    pagination = query.paginate(page=page, per_page=10, error_out=False)
    incidentes = pagination.items
    
    return render_template('encargado_de_convivencia/general_explorar_antecedentes.html', incidentes=incidentes, pagination=pagination, filtro=filtro)


@encargado.route('/nuevoCaso', methods=["GET", "POST"])
@login_required("encargado_de_convivencia")
def nuevoCaso():
    if request.method == "POST":
        nombre_caso = request.form.get('nombre_caso')
        ids_seleccionados = request.form.getlist('antecedentes_seleccionados')
        
        # ESCENARIO 1: El usuario envió el formulario final para guardar el caso
        # (Sabemos esto porque la llave 'nombre_caso' viene en la petición POST)
        if 'nombre_caso' in request.form:
            
            # Restauramos la validación que faltaba
            if not nombre_caso or not nombre_caso.strip():
                flash("El nombre del caso es obligatorio.", "warning")
                # Si faltó el nombre, recargamos la página
                return render_template('encargado_de_convivencia/caso_nuevo.html', preseleccionados=ids_seleccionados, cantidad=len(ids_seleccionados))
            
            # Si el nombre es válido, inicializamos
            nuevo_caso = Caso(
                nombre=nombre_caso.strip(),
                encargado_id=session.get('user_id')
            )
            
            # Vinculamos los incidentes si venían preseleccionados
            if ids_seleccionados:
                evidencias = Antecedente.query.filter(Antecedente.id.in_(ids_seleccionados)).all()
                for ev in evidencias:
                    nuevo_caso.evidencias.append(ev)
            
            try:
                db.session.add(nuevo_caso)
                db.session.commit()
                flash(f"El caso '{nombre_caso}' ha sido abierto exitosamente.", "success")
                return redirect(url_for('encargado_de_convivencia.misCasos'))
            except Exception as e:
                db.session.rollback()
                flash("Ocurrió un error al intentar crear el caso.", "danger")
                print(f"Error: {e}")
                return redirect(url_for('encargado_de_convivencia.nuevoCaso'))
                
        # ESCENARIO 2: Llegando desde el Explorador (Aún no envía 'nombre_caso')
        elif ids_seleccionados:
            cantidad_preseleccionada = len(ids_seleccionados)
            return render_template('encargado_de_convivencia/caso_nuevo.html', preseleccionados=ids_seleccionados, cantidad=cantidad_preseleccionada)

    # ESCENARIO 3: GET normal
    return render_template('encargado_de_convivencia/caso_nuevo.html', preseleccionados=[], cantidad=0)


@encargado.route('/misCasos', methods=["GET"])
@login_required("encargado_de_convivencia")
def misCasos():
    usuario_actual = session.get('user_id')
    
    # Paginación separada para abiertos y cerrados
    page_abiertos = request.args.get('page_abiertos', 1, type=int)
    page_cerrados = request.args.get('page_cerrados', 1, type=int)
    
    # Consultamos con paginación
    pagination_abiertos = Caso.query.filter_by(
        estado='ABIERTO', 
        encargado_id=usuario_actual
    ).order_by(Caso.fecha_creacion.desc()).paginate(page=page_abiertos, per_page=10, error_out=False)
    
    pagination_cerrados = Caso.query.filter(
        Caso.estado != 'ABIERTO', 
        Caso.encargado_id == usuario_actual
    ).order_by(Caso.fecha_creacion.desc()).paginate(page=page_cerrados, per_page=10, error_out=False)

    return render_template('encargado_de_convivencia/mis_casos.html', 
                           pagination_abiertos=pagination_abiertos,
                           pagination_cerrados=pagination_cerrados,
                           casos_abiertos=pagination_abiertos.items,
                           casos_cerrados=pagination_cerrados.items)


@encargado.route('/caso/<int:caso_id>', methods=["GET", "POST"])
@login_required("encargado_de_convivencia")
def detalleCaso(caso_id):
    # Obtener el caso de la BD. Si no existe, lanza un error 404 automáticamente.
    caso = Caso.query.get_or_404(caso_id)
    
    # Validación de seguridad: Asegurarse de que el caso le pertenece a este encargado
    if caso.encargado_id != session.get('user_id'):
        flash("No tienes permiso para ver o editar este caso.", "danger")
        return redirect(url_for('encargado_de_convivencia.misCasos'))

    # Si se envía el formulario para cambiar el estado
    if request.method == "POST":
        nuevo_estado = request.form.get('estado_caso')
        
        # Validar que el estado enviado sea uno de los permitidos
        if nuevo_estado in ['ABIERTO', 'RESUELTO', 'ARCHIVADO']:
            caso.estado = nuevo_estado
            try:
                db.session.commit()
                flash(f"El estado del caso ha sido actualizado a {nuevo_estado}.", "success")
            except Exception as e:
                db.session.rollback()
                flash("Error al actualizar el estado del caso.", "danger")
                print(f"Error: {e}")
                
        return redirect(url_for('encargado_de_convivencia.detalleCaso', caso_id=caso.id))

    return render_template('encargado_de_convivencia/caso_detalles.html', caso=caso)


@encargado.route('/caso/<int:caso_id>/vincular', methods=["GET", "POST"])
@login_required("encargado_de_convivencia")
def vincularEvidencia(caso_id):
    caso = Caso.query.get_or_404(caso_id)
    
    # Validación de seguridad: el caso debe pertenecer al encargado en sesión
    if caso.encargado_id != session.get('user_id'):
        flash("No tienes permiso para editar este caso.", "danger")
        return redirect(url_for('encargado_de_convivencia.misCasos'))

    if request.method == "POST":
        # request.form.getlist atrapa todos los checkboxes seleccionados
        ids_seleccionados = request.form.getlist('antecedentes_seleccionados')
        
        if not ids_seleccionados:
            flash("No se seleccionó ningún antecedente para vincular.", "warning")
            return redirect(url_for('encargado_de_convivencia.vincularEvidencia', caso_id=caso.id))

        # Buscamos los antecedentes seleccionados en la BD
        antecedentes_a_vincular = Antecedente.query.filter(Antecedente.id.in_(ids_seleccionados)).all()

        # Los agregamos a la relación. SQLAlchemy maneja la tabla intermedia automáticamente
        for ant in antecedentes_a_vincular:
            if ant not in caso.evidencias:
                caso.evidencias.append(ant)

        try:
            db.session.commit()
            flash(f"Se vincularon {len(antecedentes_a_vincular)} evidencias al caso exitosamente.", "success")
        except Exception as e:
            db.session.rollback()
            flash("Ocurrió un error al vincular la evidencia.", "danger")
            print(f"Error: {e}")

        # Volvemos a la vista de detalles para ver los cambios reflejados
        return redirect(url_for('encargado_de_convivencia.detalleCaso', caso_id=caso.id))

    # GET: Obtenemos todos los antecedentes del sistema para mostrarlos con paginación
    # (Para no duplicar visualmente, omitimos los que ya están en el caso)
    page = request.args.get('page', 1, type=int)
    
    # Obtener todos primero para filtrar
    todos_los_antecedentes = Antecedente.query.order_by(Antecedente.fecha_adicion.desc()).all()
    antecedentes_disponibles = [a for a in todos_los_antecedentes if a not in caso.evidencias]
    
    # Calcular paginación manualmente (ya que es una lista filtrada)
    per_page = 10
    total = len(antecedentes_disponibles)
    pages = (total + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    antecedentes_pagina = antecedentes_disponibles[start:end]
    
    return render_template('encargado_de_convivencia/explorar_antecedentes.html', 
                          caso=caso, 
                          antecedentes=antecedentes_pagina,
                          page=page,
                          pages=pages,
                          total=total)

@encargado.route('/estudiante/<int:estudiante_id>/expediente')
@login_required("encargado_de_convivencia")
def expedienteEstudiante(estudiante_id):

    # =========================
    # ESTUDIANTE
    # =========================

    estudiante = Estudiante.query.get_or_404(estudiante_id)

    # =========================
    # ANTECEDENTES
    # =========================

    antecedentes = estudiante.antecedentes

    # =========================
    # INCIDENTES
    # =========================

    incidentes = [
        a for a in antecedentes
        if isinstance(a, Incidente)
    ]

    incidentes.sort(
        key=lambda x: x.fecha_adicion,
        reverse=True
    )

    # =========================
    # CASOS RELACIONADOS
    # =========================

    casos = []

    for antecedente in antecedentes:

        for caso in antecedente.casos_asociados:

            if caso not in casos:
                casos.append(caso)

    casos.sort(
        key=lambda x: x.fecha_creacion,
        reverse=True
    )

    # =========================
    # HISTORIAL
    # =========================

    historial = antecedentes

    historial.sort(
        key=lambda x: x.fecha_adicion,
        reverse=True
    )

    # =========================
    # PAGINACIÓN
    # =========================
    
    page_incidents = request.args.get('page_incidents', 1, type=int)
    page_cases = request.args.get('page_cases', 1, type=int)
    
    per_page = 10
    
    # Paginación incidentes
    total_incidents = len(incidentes)
    pages_incidents = (total_incidents + per_page - 1) // per_page
    start = (page_incidents - 1) * per_page
    end = start + per_page
    incidentes_pagina = incidentes[start:end]
    
    # Paginación casos
    total_cases = len(casos)
    pages_cases = (total_cases + per_page - 1) // per_page
    start = (page_cases - 1) * per_page
    end = start + per_page
    casos_pagina = casos[start:end]

    return render_template(
        'encargado_de_convivencia/expediente_estudiante.html',
        student=estudiante,
        incidents=incidentes_pagina,
        cases=casos_pagina,
        history=historial,
        page_incidents=page_incidents,
        pages_incidents=pages_incidents,
        total_incidents=total_incidents,
        page_cases=page_cases,
        pages_cases=pages_cases,
        total_cases=total_cases
    )


@encargado.route('/incidente/<int:incidente_id>')
@login_required("encargado_de_convivencia")
def verIncidente(incidente_id):
    # Usamos Antecedente para que la vista soporte cualquier tipo de registro en el futuro
    incidente = Antecedente.query.get_or_404(incidente_id)
    return render_template('encargado_de_convivencia/incidente_detalles.html', incidente=incidente)