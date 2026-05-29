def test_database_connection(client, init_database):
    # La base de datos y el cliente ya están inicializados por pytest
    response = client.get('/test-db')
    
    assert response.status_code == 200
    
    data = response.get_json()
    assert data["status"] == "Conexión exitosa"