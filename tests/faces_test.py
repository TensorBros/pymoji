"""see pymoji/faces.py"""
import os

from PIL import Image

from pymoji.constants import DEMO_PATH, OUTPUT_DIR
from pymoji import faces, utils


def test_detect_faces():
    """tests pymoji.faces.detect_faces"""

    def assert_valid_demo_face(face):
        """Test assertion helper"""
        assert face.detection_confidence >= 0.99
        assert face.joy_likelihood == 1
        assert face.headwear_likelihood == 5
        # bounding box detection varies, use approximate math
        assert abs(face.bounding_poly.vertices[0].x - 395) < 10
        assert abs(face.bounding_poly.vertices[0].y - 178) < 10

    # test local image source
    with open(DEMO_PATH, 'rb') as input_file:
        face = faces.detect_faces(input_stream=input_file)[0]
        assert_valid_demo_face(face)

    # test remote image uri
    input_uri = 'gs://pymoji-176318/uploads/face-input.jpg'
    face = faces.detect_faces(input_uri=input_uri)[0]
    assert_valid_demo_face(face)


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
