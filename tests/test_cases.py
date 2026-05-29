from app.db_model import Caso

def test_create_case_page_loads(client, init_database, auth_manager):
    # auth_manager simula la sesión automáticamente
    response = client.get('/manager/nuevoCaso')
    assert response.status_code == 200


def test_case_requires_name(client, init_database, auth_manager):
    response = client.post(
        '/manager/nuevoCaso',
        data={
            "nombre_caso": ""
        },
        follow_redirects=True
    )
    
    assert response.status_code == 200
    assert b"obligatorio" in response.data


def test_create_case_successfully(client, init_database, auth_manager):
    response = client.post(
        '/manager/nuevoCaso',
        data={
            "nombre_caso": "Caso bullying"
        },
        follow_redirects=True
    )
    
    assert response.status_code == 200
    assert b"ha sido abierto" in response.data

    assert Caso.query.count() == 1
    caso_guardado = Caso.query.first()
    assert caso_guardado.nombre == "Caso bullying"
    assert caso_guardado.estado == 'ABIERTO'

    assert caso_guardado.encargado_id == 2
