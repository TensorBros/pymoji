"""see pymoji/faces.py"""
import os

from PIL import Image

from pymoji.constants import DEMO_PATH, OUTPUT_DIR
from pymoji import faces, utils


def test_process_path():
    """tests pymoji.faces.process_path"""

    # Make sure there isn't already any emoji-yellow
    image = Image.open(DEMO_PATH)
    pixels = image.getdata()
    unnatural_face_yellow = sum(1 for (r, g, b) in pixels if r == 251 and g == 200 and b == 83)
    assert unnatural_face_yellow < 1

    id_filename = faces.process_path(DEMO_PATH)
    output_filename = utils.get_output_name(id_filename)
    out_path = os.path.join(OUTPUT_DIR, output_filename)

    # Make sure there now is some emoji-yellow drawn
    image = Image.open(out_path)
    pixels = image.getdata()
    unnatural_face_yellow = sum(1 for (r, g, b) in pixels if r == 251 and g == 200 and b == 83)
    assert unnatural_face_yellow > 4


def test_process_local():
    """ tests pymoji.faces.process_local"""
    pass


def test_process_cloud():
    """ tests pymoji.faces.process_cloud"""
    pass
