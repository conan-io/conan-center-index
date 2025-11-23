async def test_kv(service_client):
    response = await service_client.post(
        '/kv',
        json={'key': 1, 'value': 'one'},
    )
    assert response.status == 200
    assert 'application/json' in response.headers['Content-Type']

    response = await service_client.get('/kv', json={'key': 1})
    assert response.status == 200
    assert response.json() == {'key': 1, 'value': 'one'}
    assert 'application/json' in response.headers['Content-Type']
