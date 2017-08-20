"""Script manager for running locally. Gunicorn is used to run the
application on Google App Engine. See entrypoint in app.yaml.
"""
import os

from flask_script import Manager

from pymoji import faces, utils
from pymoji.app import APP
from pymoji.constants import OUTPUT_DIR, STATIC_DIR


MANAGER = Manager(APP)


@MANAGER.command
def runface(input_image=None, output_image=None):
    """Processes faces in the specified image.

    Args:
        input_image: name of image resource file to process faces in.
        output_image: name of output file to write modified image to. (optional)
    """
    input_path = os.path.join(STATIC_DIR, input_image)

    if output_image:
        output_path = os.path.join(OUTPUT_DIR, output_image)
    else:
        output_path = utils.generate_output_path(input_image)

    faces.main(input_path, output_path)


@MANAGER.command
def runfolder(directory=None):
    """Processes images in the specified directory.

    Args:
        directory: path to directory to process images in.
    """
    utils.process_folder(directory, faces.main)


if __name__ == "__main__":
    MANAGER.run()
