from app import create_app


def test_students_page_loads():

    app = create_app()

    with app.test_client() as client:

        response = client.get('/students')

        assert response.status_code == 200
