from flask import Blueprint, render_template

reportador = Blueprint('reportador', __name__)

@reportador.route('/')
def home():
  return render_template('reporter_home.html')

@reportador.route('/reportarIncidente', methods=["GET"])
def nuevoReporte():
  return render_template('components/search_students.html') # por ahora solo el buscador