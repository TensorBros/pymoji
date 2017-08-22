"""Script manager for running locally. Gunicorn is used to run the
application on Google App Engine. See entrypoint in app.yaml.
"""
from flask_script import Manager

from pymoji.app import APP
from pymoji.faces import process_path
from pymoji.utils import process_folder


MANAGER = Manager(APP)


@MANAGER.command
def runface(image_path):
    """Processes faces in the given image.

    Args:
        image_path: path to an image file to process faces in.
    """
    process_path(image_path)


@MANAGER.command
def rundir(directory_path):
    """Processes images in the given directory.

    Args:
        directory_path: path to a directory to process images in.
    """
    process_folder(directory_path, process_path)


if __name__ == "__main__":
    MANAGER.run()
