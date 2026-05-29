from flask import Blueprint, render_template, session, request, flash, redirect, url_for
from app.auth.login_required import login_required
from app.db_model import db, Estudiante, Curso, Incidente, Caso, Antecedente
from app.queries import ejecutar_consulta

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
        query_cursos = Curso.query.order_by(Curso.nombre.asc()).all()

        q = request.args.get('q')
        curso = request.args.get('curso')
        estudiantes = ejecutar_consulta("buscar_estudiantes", {"q": q, "curso": curso, "raw": True})

        return render_template('components/search_students.html',
                               EstudianteCurso_todos=estudiantes,
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


@manager.route('/explorarIncidentes', methods=["GET"])
@login_required("encargado_de_convivencia")
def explorarIncidentes():
    # Obtenemos el filtro por GET (si no existe, por defecto es 'todos')
    filtro = request.args.get('filtro', 'todos')
    
    # Consultamos exclusivamente los Incidentes
    query = Incidente.query.order_by(Incidente.fecha_adicion.desc())
    
    # Aplicamos el filtro si el usuario quiere ver solo los suyos
    if filtro == 'mios':
        query = query.filter_by(creador_id=session.get('user_id'))
        
    incidentes = query.all()
    
    return render_template('general_explore_incidents.html', incidentes=incidentes, filtro=filtro)


@manager.route('/nuevoCaso', methods=["GET", "POST"])
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
                return render_template('new_case.html', preseleccionados=ids_seleccionados, cantidad=len(ids_seleccionados))
            
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
            return render_template('new_case.html', preseleccionados=ids_seleccionados, cantidad=cantidad_preseleccionada)

    # ESCENARIO 3: GET normal
    return render_template('new_case.html', preseleccionados=[], cantidad=0)


@manager.route('/misCasos', methods=["GET"])
@login_required("encargado_de_convivencia")
def misCasos():
    usuario_actual = session.get('user_id')
    
    # Consultamos solo los casos que le pertenecen al encargado actual
    casos_abiertos = Caso.query.filter_by(
        estado='ABIERTO', 
        encargado_id=usuario_actual
    ).order_by(Caso.fecha_creacion.desc()).all()
    
    casos_cerrados = Caso.query.filter(
        Caso.estado != 'ABIERTO', 
        Caso.encargado_id == usuario_actual
    ).order_by(Caso.fecha_creacion.desc()).all()

    return render_template('my_cases.html', 
                           casos_abiertos=casos_abiertos, 
                           casos_cerrados=casos_cerrados)


@manager.route('/caso/<int:caso_id>', methods=["GET", "POST"])
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

    return render_template('case_detail.html', caso=caso)


@manager.route('/caso/<int:caso_id>/vincular', methods=["GET", "POST"])
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

    # GET: Obtenemos todos los antecedentes del sistema para mostrarlos
    # (Para no duplicar visualmente, omitimos los que ya están en el caso)
    todos_los_antecedentes = Antecedente.query.order_by(Antecedente.fecha_adicion.desc()).all()
    antecedentes_disponibles = [a for a in todos_los_antecedentes if a not in caso.evidencias]

    return render_template('explore_incidents.html', caso=caso, antecedentes=antecedentes_disponibles)

@manager.route('/estudiante/<int:estudiante_id>/expediente')
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

    return render_template(
        'student_record.html',
        student=estudiante,
        incidents=incidentes,
        cases=casos,
        history=historial
    )


@manager.route('/incidente/<int:incidente_id>')
@login_required("encargado_de_convivencia")
def verIncidente(incidente_id):
    # Usamos Antecedente para que la vista soporte cualquier tipo de registro en el futuro
    incidente = Antecedente.query.get_or_404(incidente_id)
    return render_template('incident_detail.html', incidente=incidente)