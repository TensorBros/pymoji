"""see pymoji/app.py"""
from pymoji.app import APP


def test_index():
    """tests pymoji.app.index"""
    APP.testing = True
    client = APP.test_client()

    response = client.get('/')
    assert response.status_code == 200
    assert u'✨📸🕶✨' in response.data.decode('utf-8')
