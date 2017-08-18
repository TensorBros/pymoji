# -*- coding: utf-8 -*-
#!/usr/bin/env python
from __future__ import absolute_import, print_function, unicode_literals
import logging
import os

from flask import Flask


RESOURCES = os.path.join('pymoji', 'static')
OUTPUT_DIR = os.path.join(RESOURCES, 'gen')

app = Flask(__name__)


@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    return '👋 🌎!'


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
