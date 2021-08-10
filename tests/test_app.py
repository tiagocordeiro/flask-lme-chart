from flask import url_for
from dotenv import load_dotenv

load_dotenv()


def test_status_code_index(client):
    assert client.get(url_for('index')).status_code == 302


def test_status_code_grafico(client):
    assert client.get(url_for('grafico')).status_code == 302


def test_status_code_cotacao(client):
    assert client.get(url_for('lme_cotacao')).status_code == 302


def test_status_code_summary(client):
    assert client.get(url_for('summary')).status_code == 302
