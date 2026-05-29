from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(user_type):

    """
    Verifica que el usuario haya iniciado sesión y tenga permisos
    para acceder a una ruta específica.
    """

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            # Usuario no autenticado
            if 'user_id' not in session:

                flash(
                    'Debe iniciar sesión para acceder a esta página.',
                    'warning'
                )

                return redirect(url_for('auth.signin'))

            # Usuario autenticado pero sin permisos
            elif session['user_type'] != user_type:

                flash(
                    'No tiene permiso para acceder a esta página.',
                    'warning'
                )

                # Redirige segun el rol

                if session['user_type'] == "reportador":

                    return redirect(
                        url_for('reportador.home')
                    )

                elif session['user_type'] == "encargado_de_convivencia":

                    return redirect(
                        url_for('encargado_de_convivencia.home')
                    )

                elif session['user_type'] == "orientador":

                    return redirect(
                        url_for('orientador.home')
                    )

                return redirect(url_for('auth.signin'))

            return func(*args, **kwargs)

        return wrapper

    return decorator