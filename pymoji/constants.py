import os


# Project directory paths
PACKAGE_DIR = 'pymoji'
STATIC_DIR = os.path.join(PACKAGE_DIR, 'static')
EMOJI_DIR = os.path.join(STATIC_DIR, 'emoji')
OUTPUT_DIR = os.path.join(STATIC_DIR, 'gen')
TEMP_FILENAME = 'face-input.jpg'
TEMP_PATH = os.path.join(STATIC_DIR, TEMP_FILENAME)
OUTPUT_PATH = os.path.join(OUTPUT_DIR, 'face-input-output.jpg')
