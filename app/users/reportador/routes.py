from flask import Blueprint, render_template, request, jsonify, abort
from app.auth.login_required import login_required
from app.queries import listar_consultas, ejecutar_consulta

reportador = Blueprint('reportador', __name__)

@reportador.route('/')
@login_required("reportador")
def home():
  return render_template('reporter_home.html')

@reportador.route('/reportarIncidente', methods=["GET"])
@login_required("reportador")
def nuevoReporte():
  return render_template('components/search_students.html') # por ahora solo el buscador

@reportador.route('/consultas', methods=["GET"])
@login_required("reportador")
def listar_consultas_route():
    return jsonify(listar_consultas())

@reportador.route('/consultas/run', methods=["GET"])
@login_required("reportador")
def ejecutar_consulta_route():
    tipo = request.args.get("tipo")
    if not tipo:
        abort(400)

    resultados = ejecutar_consulta(tipo, request.args.to_dict())
    return jsonify(resultados)