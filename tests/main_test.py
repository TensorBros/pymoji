# -*- coding: utf-8 -*-
from pymoji.app import app


def test_index():
    app.testing = True
    client = app.test_client()

    r = client.get('/')
    assert r.status_code == 200
    assert u'✨📸🕶✨' in r.data.decode('utf-8')
