
from app import create_app


def test_database_connection():

    app = create_app()

    with app.test_client() as client:

        response = client.get('/test-db')

        assert response.status_code == 200

        data = response.get_json()

        assert data["status"] == "Conexión exitosa"
