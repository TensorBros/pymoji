"""Common utility functions.

https://docs.python.org/3/tutorial/inputoutput.html
https://docs.python.org/3/library/io.html
"""
from io import BytesIO
import os
import time
import logging

import exifread
from google.cloud import storage, error_reporting
from PIL import Image
import requests
from requests.exceptions import Timeout
from werkzeug.utils import secure_filename

from pymoji import PROJECT_ID
from pymoji.models import AnnotationsSchema
from pymoji.constants import (ALLOWED_EXTENSIONS, PYMOJI_WEBHOOK_USERNAME,
    PYMOJI_WEBHOOK_ICON, PYMOJI_WEBHOOK_URL)

def average_points(a, b):
  '''Takes a point object and returns the averaged location

  Args:
    point: a dictionary of position with an x and y coordinate
  '''
  avg = { 'x' : (a.x + b.x)/2, 'y': (a.y + b.y)/2}

  return avg

def shell(cmd, fail_on_error=True):
    """Convenience wrapper function."""
    print(cmd)
    result = os.system(cmd)
    if fail_on_error and result:
        print("Error code: {}".format(result))
        raise Exception("Error in script:\n{0}".format(cmd))
    return result


def allowed_file(filename):
    """Checks if the given filename matches the allowed extensions.

    http://flask.pocoo.org/docs/0.12/patterns/fileuploads/

    Args:
        filename: a string.

    Result:
        True iff the filename is allowed.
    """
    _, extension = os.path.splitext(filename)
    clean_extension = extension.split('.')[-1].lower()
    return clean_extension in ALLOWED_EXTENSIONS


def save_to_cloud(data_stream, filename, content_type):
    """Saves the data in the given IO stream to the Google Storage Cloud and
    returns the new public URL.

    https://cloud.google.com/appengine/docs/flexible/python/using-cloud-storage

    Args:
        data_stream: an IO stream object with read access
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
        data_stream.read(),
        content_type=content_type
    )

    print('...upload completed.')
    # The public URL can be used to directly access the uploaded file via HTTP.
    return blob.public_url

def report_upload_to_slack(id_filename):
    """Webhook to let Slack know someone has uploaded to our google cloud.
    If this hook fails it times out after 0.5 seconds.

    Args:
        id_filename: the link-about filename we've created to store and reference this upload

    Returns:
        an integer status code
    """
    url = PYMOJI_WEBHOOK_URL
    msg_raw = "At {time}, someone uploaded:\n<http://tensorbros.com/emojivision/{file}|{file}>"
    msg = msg_raw.format(time=timestamp_for_logs(), file=id_filename)
    payload = {
      "text": msg,
      "username": PYMOJI_WEBHOOK_USERNAME,
      "icon_emoji": PYMOJI_WEBHOOK_ICON
      }
    headers = {'content-type': 'application/json'}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=0.5)
        status = response.status_code
    except Timeout:
        # log the error to google's stackdriver TODO: abstract this
        error_client = error_reporting.Client(project=PROJECT_ID)
        error_client.report_exception()
        logging.error('A timeout occurred during an external request to Slack.')

        # Request Timeout https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.9
        status = 408

    return status

def write_json(annotation_data, json_stream):
    """Serializes the given metadata object with marshmallow and writes the
    resulting JSON string to the given TextIO stream.

    Args:
        annotation_data: a metadata object matching models.AnnotationsSchema
        json_stream: a TextIO stream with write access to write JSON to
    """
    schema = AnnotationsSchema()
    result = schema.dumps(annotation_data)
    json_stream.write(result.data)


def load_json(json_stream):
    """Deserializes the JSON metadata from the given TextIO stream using
    marshmallow and returns the resulting object.

    Args:
        json_stream: a TextIO stream with read access containing the JSON metadata

    Returns:
        a metadata object matching models.AnnotationsSchema
    """
    schema = AnnotationsSchema()
    result = schema.loads(json_stream.read())
    return result.data


def download_json(json_uri):
    """Downloads the JSON metadata at the given URI, deserializes it with
    marshmallow, and returns the resulting object.

    http://docs.python-requests.org/en/master/user/quickstart/

    Args:
        image_uri: an metadata uri, e.g. 'http://cdn/path/to/image-meta.json'

    Returns:
        a metadata object based on annotations from the Google Vision API.
    """
    print('Downloading metadata: {} ...'.format(json_uri))
    response = requests.get(json_uri)
    print('...download completed.')
    schema = AnnotationsSchema()
    result = schema.loads(response.text)
    return result.data


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


def orient_image(input_stream, output_stream):
    """Rotates the image in the given BufferedIO based on its EXIF orientation
    metadata, then exports the result to the given destination BufferedIO.

    https://stackoverflow.com/questions/4228530/pil-thumbnail-is-rotating-my-image

    Args:
        input_stream: a BufferedIO image file-object with EXIF metadata
        output_stream: a file-object to save the result to
    """
    tags = []
    tags = exifread.process_file(input_stream)
    input_stream.seek(0) # Reset the file pointer, so we can read the file again

    image = Image.open(input_stream)
    orientation_key = 'Image Orientation'
    if tags and orientation_key in tags:
        orientation_tag = tags[orientation_key]
        if orientation_tag.values:
            tag_value = orientation_tag.values[0] # assume this for now???
            if tag_value == 3:
                image = image.rotate(180, expand=True)
                print('rotated image 180 degrees')
            elif tag_value == 6:
                image = image.rotate(270, expand=True)
                print('rotated image 270 degrees')
            elif tag_value == 8:
                image = image.rotate(90, expand=True)
                print('rotated image 90 degrees')

    image.save(output_stream)
    image.close()


def get_id_name(filename):
    """Makes a safe, unique-ish filename based on the given input filename.

    Args:
        input_filename: a filname string, e.g. "face-input.jpg"

    Returns:
        a unique-ish filename string, e.g. "1503280514351_face-input.jpg"
    """
    timestamp_in_seconds = int(round(time.time() * 1000))
    return str(timestamp_in_seconds) + '_' + secure_filename(filename)

def timestamp_for_logs():
    """Returns consistent timestamp for the app logs
    """
    return time.strftime('%A, %d %b %Y %l:%M %p')

def get_json_name(input_filename):
    """Makes a faces metadata filename based on the given input filename.

    Args:
        input_filename: a filname string, e.g. "face-input.jpg"

    Returns:
        a filename string, e.g. "face-input-meta.json"
    """
    root, _ = os.path.splitext(input_filename)
    return "{}-meta.json".format(root)


def get_output_name(input_filename):
    """Makes an output filename based on the given input filename.

    Args:
        input_filename: a filname string, e.g. "face-input.jpg"

    Returns:
        a filename string, e.g. "face-input-output.jpg"
    """
    root, extension = os.path.splitext(input_filename)
    return "{}-output{}".format(root, extension)


def process_folder(path, file_processor):
    """Runs the given file processing operation on each image in
    the given directory.

    Args:
        path: a directory path string
        file_processor: a function(input_path) to run on each image
    """
    print('processing directory {} ...'.format(path))
    for file_name in os.listdir(path):
        print('processing file {} ...'.format(file_name))
        file_path = os.path.join(path, file_name)
        try:
            file_processor(file_path)
        except IOError as error:
            print('bad image: %s' % error)
