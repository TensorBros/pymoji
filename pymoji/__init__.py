"""Initializes and configures the Emojivision web app."""
import logging

from flask import Flask
import google.cloud.logging


APP = Flask(__name__, instance_relative_config=True)
APP.config.from_pyfile('config.py')
# would then override with settings found in file at env var
#APP.config.from_envvar('YOURAPPLICATION_SETTINGS')

# convenience references for other modules to import
MAX_RESULTS = APP.config['MAX_RESULTS']
PROJECT_ID = APP.config['PROJECT_ID']

# Configure logging
if not APP.testing:
    LOGGER = google.cloud.logging.Client(project=PROJECT_ID)
    # Attaches a Google Stackdriver logging handler to the root logger
    LOGGER.setup_logging(logging.INFO)
