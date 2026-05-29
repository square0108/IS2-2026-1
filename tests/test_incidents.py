def test_report_page_loads(client, init_database, auth_reportador):
    response = client.get('/reportador/reportarIncidente')
    assert response.status_code == 200


def test_incident_requires_required_fields(client, init_database, auth_reportador):
    response = client.post(
        '/reportador/reportarIncidente',
        data={
            "categoria_incidente": "",
            "descripcion": "",
            "id_estudiantes_involucrados": []
        },
        follow_redirects=True
    )
    
    assert response.status_code == 200
    assert b"Error" in response.data


def test_create_incident_successfully(client, init_database, auth_reportador):
    response = client.post(
        '/reportador/reportarIncidente',
        data={
            "categoria_incidente": "verbal",  # Ajustado al select del form
            "descripcion": "Discusion entre estudiantes",
            "respuesta_inmediata": "Separacion inmediata",
            "id_estudiantes_involucrados": [1]
        },
        follow_redirects=True
    )
    
    assert response.status_code == 200
    assert b"exitosamente" in response.data
