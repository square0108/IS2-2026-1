from flask import Blueprint, render_template, request, flash, redirect, url_for, session

auth = Blueprint('auth', __name__)

from app.db_model import db, Usuario

# Pagina de login
@auth.route('/', methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        # Enviados por el usuario en la interfaz
        form_username = request.form.get("username")
        form_password = request.form.get("password")

        # no se si es bueno hacer queries ORM directo en los endpoints, pero bueno
        queried_user = Usuario.query.filter_by(username=form_username).first()
        print(queried_user)

        if queried_user and queried_user.check_password(form_password): # cambiar esto a un mejor check de null?
            # Store essential user data in the session cookie
            session["user_id"] = queried_user.id
            session["user_name"] = queried_user.nombre_completo
            
            if queried_user.es_encargado:
                session["user_type"] = "encargado_de_convivencia"
                return redirect(url_for("encargado_de_convivencia.home"))

            elif queried_user.es_reportador:
                session["user_type"] = "reportador"
                return redirect(url_for("reportador.home"))
                
        else:
            flash("Usuario o contraseña incorrectos", "danger")
            return redirect(url_for("auth.signin"))

    elif request.method == "GET":
        return render_template("auth/signin.html")
    
@auth.route('/logout')
def signout():
    session.clear()
    flash("Has cerrado tu sesión")
    return redirect(url_for("auth.signin"))