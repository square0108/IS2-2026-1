from flask import Blueprint, render_template, session
from app.auth.login_required import login_required

manager = Blueprint('encargado_de_convivencia', __name__)

@manager.route('/')
@login_required("encargado_de_convivencia")
def home():
    # Renderiza el panel principal del encargado
    return render_template('manager_home.html')