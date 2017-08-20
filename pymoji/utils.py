"""Common utility functions."""
import os

import PIL

from pymoji.constants import OUTPUT_DIR


def generate_output_name(input_image):
    """Makes a filename to save the result image into.

    Args:
        input_image: a filname string, e.g. "face-input.jpg"

    Returns:
        a filename string, e.g. "face-input-output.jpg"
    """
    filename = input_image.split('.')[-2]
    extension = input_image.split('.')[-1]
    return filename + "-output." + extension


def generate_output_path(input_image):
    """Makes a path to save the result image into.

    Args:
        input_image: A string, eg "face-input.jpg"

    Returns:
        "pymoji/static/gen/face-input-output.jpg"
    """
    output_image = generate_output_name(input_image)
    return os.path.join(OUTPUT_DIR, output_image)


def process_folder(path, file_processor):
    """Runs the specified file processing operation on each JPG in
    the specified directory.

    Args:
        path: a directory path string
        file_processor: a function(input_path, output_path) to run
            on each JPG
    """
    for file_name in os.listdir(path):
        actual_file_location = os.path.join(path, file_name)
        is_jpg = (os.path.splitext(file_name)[1] == '.jpg' or
            os.path.splitext(file_name)[1] == '.JPG')

        if os.path.isfile(actual_file_location) and is_jpg:
            image = PIL.Image.open(actual_file_location)
            try:
                image.load()
                print('processing ' + os.path.splitext(file_name)[0])
                output_path = generate_output_path(file_name)
                file_processor(os.path.join(path, file_name), output_path)
            except IOError as error:
                print('Bad image: %s' % error)
        else:
            print('skipped non-image file')
