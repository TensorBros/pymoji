"""Default instance application configuation settings.

To set up a local environment, start by copying this file:
  $ cp config.py instance/config.py

Then edit instance/config.py, e.g.
  DEBUG = True
  TESTING = True
  SECRET_KEY = 'a-secret-all-your-own' # change this
  #SERVER_NAME = 'tensorbros.com' # comment out for localhost
"""

# Webserver Settings
# http://flask.pocoo.org/docs/0.12/config/#builtin-configuration-values
DEBUG = False
TESTING = False # also controls local VS google cloud services
SECRET_KEY = '684cac4ebdce5226e60d5613667c8138' # change this
MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # 16MB upload limit
# EXPLAIN_TEMPLATE_LOADING = True # noisy but can be useful for debugging
SERVER_NAME = 'tensorbros.com' # comment out for localhost

# IMPORTANT: be extremely careful with this!
# Setting to True will break Google App Engine load balancers!!!
# (this probably has to do with GAE expecting a 404 at /_ah/healthcheck)
# TRAP_HTTP_EXCEPTIONS = True

# Google App Engine
PROJECT_ID = 'pymoji-176318'

# Face detection params
MAX_RESULTS = 20
