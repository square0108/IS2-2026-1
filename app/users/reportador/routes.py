from flask import Blueprint, render_template
from app.auth.login_required import login_required

reportador = Blueprint('reportador', __name__)

@reportador.route('/')
@login_required("reportador")
def home():
  return render_template('reporter_home.html')

@reportador.route('/reportarIncidente', methods=["GET"])
@login_required("reportador")
def nuevoReporte():
  return render_template('components/search_students.html') # por ahora solo el buscador