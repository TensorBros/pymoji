"""see pymoji/vision.py"""
from pymoji.constants import DEMO_PATH
from pymoji import vision


def assert_valid_demo_face(face):
    """Test assertion helper"""
    assert face.detection_confidence >= 0.99
    assert face.joy_likelihood == 1
    assert face.headwear_likelihood == 5
    # bounding box detection varies, use approximate math
    assert abs(face.bounding_poly.vertices[0].x - 395) < 10
    assert abs(face.bounding_poly.vertices[0].y - 178) < 10


def test_detect_faces():
    """tests pymoji.vision.detect_faces"""
    # assumes vision.to_vision_image works for a stream
    with open(DEMO_PATH, 'rb') as input_file:
        gv_image = vision.to_vision_image(input_stream=input_file)
        face = vision.detect_faces(gv_image)[0]
        assert_valid_demo_face(face)


def test_to_vision_image():
    """ tests pymoji.vision.to_vision_image"""
    # assumes vision.detect_faces works correctly

    # test local image source
    with open(DEMO_PATH, 'rb') as input_file:
        gv_image = vision.to_vision_image(input_stream=input_file)
        face = vision.detect_faces(gv_image)[0]
        assert_valid_demo_face(face)

    # test remote image uri
    input_uri = 'gs://pymoji-176318/uploads/face-input.jpg'
    gv_image = vision.to_vision_image(input_uri=input_uri)
    face = vision.detect_faces(gv_image)[0]
    assert_valid_demo_face(face)


def test_detect_labels():
    """ tests pymoji.vision.detect_labels"""
    # assumes vision.to_vision_image works for a stream
    with open(DEMO_PATH, 'rb') as input_file:
        gv_image = vision.to_vision_image(input_stream=input_file)
        labels = vision.detect_labels(gv_image)
        found_glasses = False
        for label in labels:
            if label.description == "glasses" and label.score > 0.7:
                found_glasses = True
                continue
        assert found_glasses
