# -*- coding: utf-8 -*-
import pymoji.app as main


def test_index():
    main.app.testing = True
    client = main.app.test_client()

    r = client.get('/')
    assert r.status_code == 200
    assert u'👋 🌎!' in r.data.decode('utf-8')
