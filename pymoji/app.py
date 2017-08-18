# -*- coding: utf-8 -*-
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
