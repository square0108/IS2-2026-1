from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(user_type):
    """ 
    Verifica que el tipo de usuario sea el que tiene permiso para acceder a la ruta. Si no,
    se redirige a la ruta de inicio de sesión.

    Parameters:
    - user_type: tipo de usuario que puede acceder estos pueden ser: 'reportador', 'encargado_de_convivencia' o 'orientador'

    Returns:
    - redirect(url_for('auth.signin')), si el usuario no tiene permisos para acceder a la página
    - nada, si el usuario si puede acceder al sitio.
    """
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'user_id' not in session:
                flash('Debe iniciar sesión para acceder a esta página.', 'warning')
                return redirect(url_for('auth.signin'))
            elif session['user_type'] != user_type:
                flash('No tiene permiso para acceder a esta página.', 'warning')
                return redirect(url_for('auth.signin'))
            return func(*args, **kwargs)
        return wrapper
    return decorator
