"""Shared constants."""
import os


# Project directory paths
PACKAGE_DIR = 'pymoji'
STATIC_DIR = os.path.join(PACKAGE_DIR, 'static')
EMOJI_DIR = os.path.join(STATIC_DIR, 'emoji')
OUTPUT_DIR = os.path.join(STATIC_DIR, 'gen')

# Google App Engine
PROJECT_ID = 'pymoji-176318'

# Face detection params
MAX_RESULTS = 20
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

# Google Vision Likelihood
# https://cloud.google.com/vision/docs/reference/rest/v1/images/annotate#likelihood
UNKNOWN = 0
VERY_UNLIKELY = 1
UNLIKELY = 2
POSSIBLE = 3
LIKELY = 4
VERY_LIKELY = 5

EMOJI_CDN_PATH = 'https://cdn.jsdelivr.net/emojione/assets/3.1/png/128/'
# backup path: 'https://api.emojione.com/emoji/1f62d/download/128/'
