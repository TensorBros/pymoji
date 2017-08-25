"""see pymoji/utils.py"""
from pymoji import utils


def test_get_extension():
    """tests pymoji.utils.get_extension"""
    assert utils.get_extension('file_wihtout_extension') == ''
    assert utils.get_extension('_input-image.foo.bar.jpg') == 'jpg'


def test_allowed_file():
    """tests pymoji.utils.allowed_file"""
    assert utils.allowed_file('.jpg')
    assert not utils.allowed_file('.mov')

def test_write_json():
    """ tests pymoji.utils.write_json"""
    pass
