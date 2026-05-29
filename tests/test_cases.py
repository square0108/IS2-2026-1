from app import create_app


def login_session(client):

    with client.session_transaction() as session:
        session["user_id"] = 1
        session["tipo_usuario"] = "encargado_de_convivencia"


def test_create_case_page_loads():

    app = create_app()

    with app.test_client() as client:

        login_session(client)

        response = client.get('/nuevoCaso')

        assert response.status_code == 200


def test_case_requires_name():

    app = create_app()

    with app.test_client() as client:

        login_session(client)

        response = client.post(
            '/nuevoCaso',
            data={
                "nombre_caso": ""
            },
            follow_redirects=True
        )

        assert response.status_code == 200

        assert b"obligatorio" in response.data


def test_create_case_successfully():

    app = create_app()

    with app.test_client() as client:

        login_session(client)

        response = client.post(
            '/nuevoCaso',
            data={
                "nombre_caso": "Caso bullying"
            },
            follow_redirects=True
        )

        assert response.status_code == 200
