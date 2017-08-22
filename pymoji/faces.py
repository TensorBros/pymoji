"""Replaces detected faces in the given image with emoji."""
import os
from tempfile import NamedTemporaryFile

from flask import url_for
from google.cloud import vision
from google.cloud.vision import types

from pymoji.constants import MAX_RESULTS, OUTPUT_DIR, PROJECT_ID, UPLOADS_DIR
from pymoji.emoji import replace_faces
from pymoji.utils import get_output_name, save_to_cloud


def detect_faces(input_content=None, input_source=None):
    """Uses the Vision API to detect faces in an input image. Pass the input
    image as a binary stream (takes precedence) or Google Cloud Storage URI.

    https://googlecloudplatform.github.io/google-cloud-python/latest/vision/index.html#annotate-an-image
    https://googlecloudplatform.github.io/google-cloud-python/latest/vision/gapic/v1/types.html#google.cloud.vision_v1.types.Image
    https://googlecloudplatform.github.io/google-cloud-python/latest/vision/gapic/v1/types.html#google.cloud.vision_v1.types.ImageSource
    https://googlecloudplatform.github.io/google-cloud-python/latest/vision/gapic/v1/types.html#google.cloud.vision_v1.types.AnnotateImageRequest
    https://googlecloudplatform.github.io/google-cloud-python/latest/vision/gapic/v1/types.html#google.cloud.vision_v1.types.Feature
    https://googlecloudplatform.github.io/google-cloud-python/latest/vision/gapic/v1/types.html#google.cloud.vision_v1.types.AnnotateImageResponse

    Args:
        input_content: a binary stream containing an image with faces.
        input_source: an image uri for either Google Cloud storage
            e.g. 'gs://bucket_name/path/to/image.jpg'
            or public http/https url
            e.g. 'http://cdn/path/to/image.jpg'

    Returns:
        an array of Face annotation objects found in the input image.
    """
    print('Detecting faces...')
    client = vision.ImageAnnotatorClient()

    # convert input image to Google Cloud Image
    content = None
    source = None
    if input_content:
        content = input_content.read()
    elif input_source:
        source = types.ImageSource(image_uri=input_source) # pylint: disable=no-member
    image = types.Image(content=content, source=source) # pylint: disable=no-member

    features = [{
        'type': vision.enums.Feature.Type.FACE_DETECTION,
        'max_results': MAX_RESULTS
    }]
    faces = client.annotate_image({
        'image': image,
        'features': features
        }).face_annotations # pylint: disable=no-member

    print('...{} faces found.'.format(len(faces)))
    return faces


def process_path(input_path, output_filename=None):
    """Processes the image at the specified input path and saves the result
    to the static output directory. Creates the output directory first if
    necessary. This is the CLI entrypoint.

    Args:
        input_path: path to source image file
        output_filename: (optional) custom filename for output file
    """
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    if not output_filename:
        input_filename = os.path.basename(input_path)
        output_filename = get_output_name(input_filename)

    output_path = os.path.join(OUTPUT_DIR, output_filename)

    with open(input_path, 'rb') as input_file:
        faces = detect_faces(input_content=input_file)
        if faces:
            print('Saving to file: {}'.format(output_path))
            input_file.seek(0) # Reset the file pointer, so we can read the file again
            replace_faces(input_file, faces, output_path)


def process_local(image, input_filename):
    """Local dev server entrypoint that processes the given image.
    Only used when APP.testing == True.

    Args:
        image: an image file-object
        input_filename: string filename of the source image

    Returns:
        tuple containing publicly accessible URLs in the form:
            (input_image_url, output_image_url)
    """
    local_input_path = os.path.join(UPLOADS_DIR, input_filename)
    print('Saving to file: {}'.format(local_input_path))
    image.save(local_input_path)

    output_filename = get_output_name(input_filename)
    process_path(local_input_path, output_filename=output_filename)

    input_image_url = url_for('static', filename='uploads/' + input_filename)
    output_image_url = url_for('static', filename='gen/' + output_filename)
    return (input_image_url, output_image_url)


def process_cloud(image, input_filename, mime):
    """Production server entrypoint that processes the given image.
    Uploads both the input and ouput images to Google Cloud Storage.
    Only used when APP.testing == False.

    Args:
        image: an image file-object
        input_filename: string filename of the source image
        mime: MIME content type string

    Returns:
        tuple containing publicly accessible URLs in the form:
            (input_image_url, output_image_url)
    """
    input_image_url = save_to_cloud(image, 'uploads/' + input_filename, mime)
    output_image_url = input_image_url

    # gs://bucket_name/object_name
    input_source = "gs://{}/uploads/{}".format(PROJECT_ID, input_filename)
    faces = detect_faces(input_source=input_source)
    if faces:
        # Use a named temp file so pillow can match input file encoding
        suffix = '.' + input_filename.rsplit('.', 1)[1]
        with NamedTemporaryFile(suffix=suffix) as output_file:
            image.seek(0) # Reset the file pointer, so we can read the file again
            replace_faces(image, faces, output_file)
            output_file.seek(0) # Reset the file pointer, so we can read the file again
            output_filename = get_output_name(input_filename)
            output_image_url = save_to_cloud(output_file, 'gen/' + output_filename, mime)

    return (input_image_url, output_image_url)
