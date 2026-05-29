from app.db_model import Incidente, Caso

def test_crear_incidente_exitoso(client, init_database, auth_manager):
    """Prueba de integración: Crear un incidente válido guarda los datos en la BD."""
    # Arrange: Nuestro fixture 'init_database' ya creó 2 estudiantes de prueba con IDs 1 y 2.
    
    # Act: Enviamos el formulario POST como si hiciéramos clic en "Registrar Incidente"
    response = client.post('/manager/reportarIncidente', data={
        'categoria_incidente': 'verbal',
        'descripcion': 'Gritos fuertes en el pasillo durante recreo.',
        'respuesta_inmediata': 'Se llamó la atención y se enviaron a sala.',
        'id_estudiantes_involucrados': [1, 2]  # Simulamos seleccionar a ambos alumnos
    }, follow_redirects=True)
    
    # Assert (Frontend): Verificamos el mensaje verde de éxito en la interfaz
    assert response.status_code == 200
    assert b'Reporte registrado exitosamente' in response.data
    
    # Assert (Backend): ¡La prueba de fuego! ¿Se guardó en la Base de Datos?
    assert Incidente.query.count() == 1
    
    incidente_guardado = Incidente.query.first()
    assert incidente_guardado.descripcion == 'Gritos fuertes en el pasillo durante recreo.'
    assert incidente_guardado.categoria == 'verbal'
    # Verificamos que la tabla intermedia vinculó correctamente a los 2 estudiantes
    assert len(incidente_guardado.estudiantes) == 2


def test_crear_incidente_faltan_datos(client, init_database, auth_manager):
    """Prueba Sad Path: Si faltan estudiantes, el sistema bloquea y no guarda nada."""
    
    # Act: Mandamos el formulario, pero omitimos la lista de estudiantes
    response = client.post('/manager/reportarIncidente', data={
        'categoria_incidente': 'fisico',
        'descripcion': 'Pelea en el patio.',
        'respuesta_inmediata': 'Separación.'
    }, follow_redirects=True)
    
    # Assert (Frontend): Vemos el mensaje de error de validación
    assert response.status_code == 200
    assert b'seleccionar al menos a un estudiante' in response.data
    
    # Assert (Backend): Confirmamos que la base de datos sigue intacta (no se guardó basura)
    assert Incidente.query.count() == 0