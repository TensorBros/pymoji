"""see pymoji/utils.py"""
from tempfile import NamedTemporaryFile
from time import sleep

from pymoji import utils
from tests import TEST_JSON_PATH


def test_allowed_file():
    """tests pymoji.utils.allowed_file"""
    assert utils.allowed_file('input-face.jpeg')
    assert utils.allowed_file('__stoo-pid.file-name.PNG')
    assert not utils.allowed_file('bar.mov')


def test_save_to_cloud():
    """ tests pymoji.utils.save_to_cloud"""
    pass


def test_write_json():
    """ tests pymoji.utils.write_json"""
    # assumes utils.load_json works correctly
    with open(TEST_JSON_PATH) as json_file:
        json_data = utils.load_json(json_file)
        with NamedTemporaryFile(suffix='.json', mode='w+') as json_stream:
            utils.write_json(json_data, json_stream)
            json_stream.seek(0)
            loaded_data = utils.load_json(json_stream)
            assert loaded_data == json_data


def test_load_json():
    """ tests pymoji.utils.load_json"""
    with open(TEST_JSON_PATH) as json_file:
        face = utils.load_json(json_file)['faces'][0]
        assert face['detection_confidence'] == 0.9950907230377197
        assert face['joy_likelihood'] == 1
        assert face['headwear_likelihood'] == 5
        assert face['bounding_poly']['vertices'][0]['x'] == 395
        assert face['bounding_poly']['vertices'][0]['y'] == 178


def test_download_json():
    """ tests pymoji.utils.download_json"""
    pass


def test_download_image():
    """ tests pymoji.utils.download_image"""
    pass


def test_orient_image():
    """ tests pymoji.utils.orient_image"""
    pass


def test_get_id_name():
    """ tests pymoji.utils.get_id_name"""
    filename = 'input-face.jpg'
    name_one = utils.get_id_name(filename)
    assert filename in name_one
    sleep(0.001)
    name_two = utils.get_id_name(filename)
    assert filename in name_two
    assert name_one != name_two
    assert name_two > name_one


def test_get_json_name():
    """ tests pymoji.utils.get_json_name"""
    assert utils.get_json_name('input-face.jpg') == 'input-face-meta.json'
    assert utils.get_json_name('__stoo-pid.file-name.PNG') == '__stoo-pid.file-name-meta.json'


def test_get_output_name():
    """ tests pymoji.utils.get_output_name"""
    assert utils.get_output_name('input-face.jpg') == 'input-face-output.jpg'
    assert utils.get_output_name('__stoo-pid.file-name.PNG') == '__stoo-pid.file-name-output.PNG'


def test_process_folder():
    """ tests pymoji.utils.process_folder"""
    pass
