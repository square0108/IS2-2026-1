def test_login_exitoso_encargado(client, init_database):
    """Prueba el Happy Path: un usuario válido inicia sesión y es redirigido a su panel."""
    # Act: Enviamos una petición POST al login con credenciales correctas
    response = client.post('/', data={
        'username': 'test.manager',
        'password': '123'
    }, follow_redirects=True)
    
    # Assert: Verificamos que cargó correctamente (200) y que vemos texto del Dashboard
    assert response.status_code == 200
    assert b'Panel de Control' in response.data or b'Panel de Gesti\xc3\xb3n' in response.data


def test_login_credenciales_invalidas(client, init_database):
    """Prueba un Sad Path: contraseña incorrecta no permite entrar."""
    # Act: Enviamos credenciales erróneas
    response = client.post('/', data={
        'username': 'test.manager',
        'password': 'clave_equivocada'
    }, follow_redirects=True)
    
    # Assert: Seguimos en la página de login y vemos el mensaje Flash de error
    assert response.status_code == 200
    assert b'Usuario o contrase\xc3\xb1a incorrectos' in response.data


def test_acceso_denegado_sin_login(client, init_database):
    """Prueba que las rutas protegidas rebotan a los visitantes anónimos."""
    # Act: Intentamos entrar directo a crear un caso sin pasar por el login
    response = client.get('/manager/nuevoCaso', follow_redirects=True)
    
    # Assert: El decorador nos debe haber pateado al login con un mensaje Flash
    assert response.status_code == 200
    assert b'Debe iniciar sesi\xc3\xb3n para acceder a esta p\xc3\xa1gina' in response.data


def test_acceso_denegado_rol_incorrecto(client, init_database, auth_reportador):
    """Prueba que un Reportador no pueda entrar a las vistas del Encargado."""
    # Arrange: El fixture 'auth_reportador' ya inyectó una sesión válida de profesor.
    
    # Act: El profesor intenta entrar a gestionar casos de convivencia
    response = client.get('/manager/nuevoCaso', follow_redirects=True)
    
    # Assert: El decorador verifica 'user_type' y lo rebota por no ser 'encargado_de_convivencia'
    assert response.status_code == 200
    assert b'No tiene permiso para acceder a esta p\xc3\xa1gina' in response.data