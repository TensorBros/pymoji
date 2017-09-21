"""Shared constants."""
import os


# Project directory paths
PACKAGE_DIR = 'pymoji'
STATIC_DIR = os.path.join(PACKAGE_DIR, 'static')
UPLOADS_DIR = os.path.join(STATIC_DIR, 'uploads')
DEMO_PATH = os.path.join(UPLOADS_DIR, 'face-input.jpg')
OUTPUT_DIR = os.path.join(STATIC_DIR, 'gen')
TEST_DATASET = os.path.join(OUTPUT_DIR, 'test_dataset.h5')
TRAIN_DATASET = os.path.join(OUTPUT_DIR, 'train_dataset.h5')

# Supported image files (Google Vision and pillow)
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

# Google Cloud Storage
CLOUD_ROOT = 'http://storage.googleapis.com/'

# Slackhook info
PYMOJI_WEBHOOK_USERNAME = 'pymoji_webhook'
PYMOJI_WEBHOOK_ICON = ':pymoji_bot:'
PYMOJI_WEBHOOK_URL = 'https://hooks.slack.com/services/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'
