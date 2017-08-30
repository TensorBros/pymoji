"""Script manager for running locally. Gunicorn is used to run the
application on Google App Engine. See entrypoint in app.yaml.
"""
from flask_script import Manager

from pymoji.app import APP
from pymoji.faces import process_path
from pymoji.utils import process_folder, shell


MANAGER = Manager(APP)


@MANAGER.command
def build():
    """test + lint

    You'll know if shit's broken first; then you'll get to hear grief about your line length
    """
    test()
    lint()


@MANAGER.command
def lint():
    """Runs all project linters on errythang!"""
    shell("pylint manage.py pymoji tests")
    #shell("static/js/node_modules/.bin/eslint --ext .js,.jsx,.json,.es6,.es static/js")


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


@MANAGER.command
def test():
    """Runs all project tests!"""
    shell("pytest")
    #shell("cd static/js && npm test")


@MANAGER.command
def install():
    """Installs all project dependencies"""
    shell("pip install -r requirements.txt")

if __name__ == "__main__":
    MANAGER.run()
