from flask import Blueprint, render_template, session, request, flash, redirect, url_for
from app.auth.login_required import login_required
from app.db_model import db, Estudiante, Curso, Antecedente, Diagnostico, Observacion, Caso

orientador = Blueprint('orientador', __name__)

@orientador.route('/')
@login_required("orientador")
def home():
    return render_template('orientador/orientador_home.html')


@orientador.route('/registrarAntecedente', methods=["GET","POST"])
@login_required("orientador")
def registrarAntecedente():
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
        if tipo_antecedente not in ['diagnostico', 'observacion']:
            flash("Tipo de registro no válido o sin permisos.", "danger")
            return redirect(url_for('orientador.registrarAntecedente'))

        # Validación Base
        if not descripcion or len(ids_estudiantes) < 1:
            flash("Error: Debe ingresar una descripción y seleccionar al menos a un estudiante.", "danger")
            return redirect(url_for('orientador.registrarAntecedente'))

        # Regla Fuerte: Diagnóstico = 1 estudiante (Protección Backend)
        if tipo_antecedente == 'diagnostico' and len(ids_estudiantes) != 1:
            flash("Error: Un diagnóstico debe estar asociado a exactamente un estudiante.", "danger")
            return redirect(url_for('orientador.registrarAntecedente'))

        estudiantes_involucrados = Estudiante.query.filter(Estudiante.id.in_(ids_estudiantes)).all()
        nuevo_antecedente = None

        # Bifurcación
        if tipo_antecedente == 'diagnostico':
            condicion = request.form.get('diagnosticoCondicion')
            if not condicion:
                flash("Error: Debe especificar la condición o diagnóstico.", "danger")
                return redirect(url_for('orientador.registrarAntecedente'))
                
            nuevo_antecedente = Diagnostico(
                descripcion=descripcion,
                condicion=condicion,
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

        return redirect(url_for('orientador.registrarAntecedente'))


@orientador.route('/explorarIncidentes')
@login_required("orientador")
def explorarIncidentes():
    return render_template('encargado_de_convivencia/explorar_antecedentes.html')


@orientador.route('/misCasos')
@login_required("orientador")
def misCasos(): # No recuerdo si decidimos que este tipo de usuario podía ver todos los casos
    casos = Caso.query.order_by(Caso.fecha_creacion.desc()).all()

    casos_abiertos = [c for c in casos if c.estado == "ABIERTO"]
    casos_cerrados = [c for c in casos if c.estado != "ABIERTO"]

    return render_template(
        'encargado_de_convivencia/mis_casos.html',
        casos_abiertos=casos_abiertos,
        casos_cerrados=casos_cerrados
    )


@orientador.route('/nuevoCaso')
@login_required("orientador")
def nuevoCaso():
    return render_template('encargado_de_convivencia/caso_nuevo.html')


@orientador.route('/diagnostico')
@login_required("orientador")
def diagnostico():
    return render_template('orientador/diagnostico.html')