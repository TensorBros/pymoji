"""Common utility functions."""
from io import BytesIO
import os
import requests

from google.cloud import storage
from PIL import Image

from pymoji.constants import ALLOWED_EXTENSIONS, OUTPUT_DIR, PROJECT_ID


def allowed_file(filename):
    """Checks if the given filename matches the allowed extensions.

    http://flask.pocoo.org/docs/0.12/patterns/fileuploads/

    Args:
        filename: a string.

    Result:
        True iff the filename is allowed.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_to_cloud(binary_file, filename, content_type):
    """Saves a binary file to the Google Storage Cloud and returns the new
    public URL.

    https://cloud.google.com/appengine/docs/flexible/python/using-cloud-storage

    Args:
        binary_file: a binary file object with read access
        filename: the desired destination filename
        content_type: MIME content type

    Returns:
        a publicly accessible URL string
    """
    print('Uploading to Google Cloud: {} ...'.format(filename))
    # Create a Cloud Storage client.
    gcs = storage.Client(project=PROJECT_ID)

    # Get the bucket that the file will be uploaded to.
    bucket = gcs.get_bucket(PROJECT_ID)

    # Create a new blob and upload the file's content.
    blob = bucket.blob(filename)

    blob.upload_from_string(
        binary_file.read(),
        content_type=content_type
    )

    print('...upload completed.')
    # The public URL can be used to directly access the uploaded file via HTTP.
    return blob.public_url


def download_image(image_uri):
    """Downloads the image at the given URI and returns it as a PIL.Image.
    Only call this on trusted URIs.

    http://pillow.readthedocs.io/en/4.2.x/reference/Image.html

    Args:
        image_uri: an image uri, e.g. 'http://cdn/path/to/image.jpg'

    Returns:
        a PIL.Image
    """
    print('Downloading source image: {} ...'.format(image_uri))
    response = requests.get(image_uri)
    print('...download completed.')
    return Image.open(BytesIO(response.content))


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
            image = Image.open(actual_file_location)
            try:
                image.load()
                print('processing ' + os.path.splitext(file_name)[0])
                output_path = generate_output_path(file_name)
                file_processor(os.path.join(path, file_name), output_path)
            except IOError as error:
                print('Bad image: %s' % error)
        else:
            print('skipped non-image file')
