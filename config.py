"""Default instance application configuation settings.

To set up a local environment, start by copying this file:
  $ cp config.py instance/local_config.py

Then edit instance/local_config.py, e.g.
  DEBUG = True
  TESTING = True
  SERVER_NAME = None

Setting values in local_config.py will override the defaults found here. Any
unspecified settings in local_config.py will simply fallback on the defaults.
"""

# Webserver Settings
# http://flask.pocoo.org/docs/0.12/config/#builtin-configuration-values

# Important for Local Dev
DEBUG = False
TESTING = False # also controls local VS google cloud services
# IMPORTANT: when running local dev environment, must override and set to None
# SERVER_NAME = None
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

# Emoji engine params
FACE_PAD = 0.05 # percentage to enlarge emoji beyond face bounding box
MAX_RESULTS = 20
USE_GVA_LABELS = True # whether or not to fallback on label analysis (slow)
