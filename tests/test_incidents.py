from app import create_app


def login_session(client):

    with client.session_transaction() as session:
        session["user_id"] = 1
        session["user_type"] = "reportador"


def test_report_page_loads():

    app = create_app()

    with app.test_client() as client:

        login_session(client)

        response = client.get('/reportador/reportarIncidente')

        assert response.status_code == 200


def test_incident_requires_required_fields():

    app = create_app()

    with app.test_client() as client:

        login_session(client)

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


def test_create_incident_successfully():

    app = create_app()

    with app.test_client() as client:

        login_session(client)

        response = client.post(
            '/reportador/reportarIncidente',
            data={
                "categoria_incidente": "Violencia",
                "descripcion": "Discusion entre estudiantes",
                "respuesta_inmediata": "Separacion inmediata",
                "id_estudiantes_involucrados": [1]
            },
            follow_redirects=True
        )

        assert response.status_code == 200
