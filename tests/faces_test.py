"""see pymoji/faces.py"""
import os

from PIL import Image

from pymoji.constants import STATIC_DIR
from pymoji.faces import process_path
from pymoji.utils import generate_output_path


def test_process_path():
    """tests pymoji.faces.process_path"""
    out_file = generate_output_path('face-input.jpg')
    in_file = os.path.join(STATIC_DIR, 'face-input.jpg')

    # Make sure there isn't already any emoji-yellow
    image = Image.open(in_file)
    pixels = image.getdata()
    unnatural_face_yellow = sum(1 for (r, g, b) in pixels if r == 251 and g == 200 and b == 83)
    assert unnatural_face_yellow < 1

    process_path(in_file)

    # Make sure there now is some emoji-yellow drawn
    image = Image.open(out_file)
    pixels = image.getdata()
    unnatural_face_yellow = sum(1 for (r, g, b) in pixels if r == 251 and g == 200 and b == 83)
    assert unnatural_face_yellow > 4
