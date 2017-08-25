"""Default instance application configuation settings.

To set up a local environment, start by copying this file:
  $ cp config.py instance/config.py

Then edit instance/config.py, e.g.
  DEBUG = True
  TESTING = True
  # IMPORTANT: must comment this out!!! ("localhost" is unsupported)
  # SERVER_NAME = 'tensorbros.com'
"""

# Webserver Settings
# http://flask.pocoo.org/docs/0.12/config/#builtin-configuration-values

# Important for Local Dev
DEBUG = False
TESTING = False # also controls local VS google cloud services
# IMPORTANT: must comment this out!!! ("localhost" is unsupported)
SERVER_NAME = 'tensorbros.com'

# Other misc Flask settings
SECRET_KEY = '684cac4ebdce5226e60d5613667c8138' # change this
MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # 16MB upload limit
# EXPLAIN_TEMPLATE_LOADING = True # noisy but can be useful for debugging
# IMPORTANT: be extremely careful with this!
# Setting to True will break Google App Engine load balancers!!!
# (this probably has to do with GAE expecting a 404 at /_ah/healthcheck)
# TRAP_HTTP_EXCEPTIONS = True


# Google App Engine
PROJECT_ID = 'pymoji-176318'

# Face detection params
MAX_RESULTS = 20
