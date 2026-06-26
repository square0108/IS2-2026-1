from app.db_model import Incidente, Caso

def test_crear_incidente_exitoso(client, init_database, auth_manager):
    """Prueba de integración: Crear un incidente válido guarda los datos en la BD."""
    
    # Act: Enviamos el formulario POST con los NUEVOS campos divididos
    response = client.post('/encargado_de_convivencia/reportarIncidente', data={
        'tipoAntecedente': 'incidente',
        'categoria_incidente': 'verbal',
        'descripcion_corta': 'Gritos fuertes',
        'descripcion_extendida': 'Gritos fuertes en el pasillo durante recreo.',
        'respuesta_inmediata': 'Se llamó la atención y se enviaron a sala.',
        'id_estudiantes_involucrados': [1, 2]
    }, follow_redirects=True)
    
    # Assert (Frontend): Verificamos el mensaje verde de éxito
    assert response.status_code == 200
    assert b'Registro guardado exitosamente' in response.data
    
    # Assert (Backend): Verificamos los nuevos campos en la BD
    assert Incidente.query.count() == 1
    incidente_guardado = Incidente.query.first()
    assert incidente_guardado.descripcion_corta == 'Gritos fuertes'
    assert incidente_guardado.descripcion_extendida == 'Gritos fuertes en el pasillo durante recreo.'
    assert incidente_guardado.categoria == 'verbal'
    assert len(incidente_guardado.estudiantes) == 2


def test_crear_incidente_faltan_datos(client, init_database, auth_manager):
    """Prueba Sad Path: Si faltan estudiantes, el sistema bloquea y no guarda nada."""
    
    response = client.post('/encargado_de_convivencia/reportarIncidente', data={
        'tipoAntecedente': 'incidente',
        'categoria_incidente': 'fisico',
        'descripcion_corta': 'Pelea en el patio',
        'descripcion_extendida': 'Pelea a golpes en el patio durante el recreo.',
        'respuesta_inmediata': 'Separación.'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'seleccionar al menos a un estudiante' in response.data
    assert Incidente.query.count() == 0