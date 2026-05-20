from flask import Blueprint, render_template, request, flash, redirect, url_for

auth = Blueprint('auth', __name__)

# Pagina de login
@auth.route('/', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        # Lógica para login
        email = request.form.get('email')
        password = request.form.get('password')
        
        # placeholder
        if email == "admin@escuela.cl" and password == "1234":
            return "Success"
        else:
            flash("Correo o contraseña incorrectos")
            return redirect(url_for('auth.signin'))

    # else if request == GET
    return render_template('signin.html')