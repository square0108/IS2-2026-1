from flask import Blueprint, render_template, session, request, flash, redirect, url_for
from app.auth.login_required import login_required
from app.db_model import db, Estudiante, Curso, Antecedente

orientador = Blueprint('orientador', __name__)

@orientador.route('/')
@login_required("orientador")
def home():
    return render_template('orientador/orientador_home.html')


@orientador.route('/listaEstudiantes', methods=["GET","POST"])
@login_required("orientador")
def listaEstudiantes():
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

        return render_template('orientador/orientador_lista_estudiantes.html',
                               EstudianteCurso_todos=estudiantes,
                               Cursos=query_cursos,
                               pagination=pagination,
                               busqueda=busquedaNombreCurso,
                               curso=curso)
    elif request.method == "POST":
        # TODO: Registrar antecedentes a la BD.
        # Args retornados por request:
        """
            'tipoAntecedente' : Uno de 'observacion' o 'diagnostico'
            Si 'tipoAntecedente' == 'diagnostico', retorna:
                'diagnosticoCondicion' : <str>
                'diagnosticoDescripcion' : <str>
            Si 'tipoAntecedente' == 'observacion', retorna:
                'observacionDescripcion' == <str>
            donde <str> es un user input escrito.
        """
        tipoAntecedente = request.form.get('tipoAntecedente')
        if tipoAntecedente == 'diagnostico':
            print(request.form.get('id_estudiantes_involucrados'))
            print(request.form.get('diagnosticoCondicion'))
            print(request.form.get('diagnosticoDescripcion'))
        return redirect(url_for('orientador.listaEstudiantes'))


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