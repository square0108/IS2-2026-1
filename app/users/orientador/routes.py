from flask import Blueprint, render_template
from app.auth.login_required import login_required
from app.db_model import Caso

orientador = Blueprint('orientador', __name__)

@orientador.route('/')
@login_required("orientador")
def home():
    return render_template('orientador/orientador_home.html')


@orientador.route('/reportarIncidente')
@login_required("orientador")
def nuevoReporte():
    return render_template('shared_components/search_students.html')


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