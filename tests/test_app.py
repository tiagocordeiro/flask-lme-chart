from flask import url_for


def test_status_code_200(client):
    assert client.get(url_for('index')).status_code == 200
