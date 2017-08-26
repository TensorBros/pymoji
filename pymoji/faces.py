"""Replaces detected faces in the given image with emoji."""
import os
from tempfile import NamedTemporaryFile

from google.cloud import vision
from google.cloud.vision import types

from pymoji import PROJECT_ID, MAX_RESULTS
from pymoji.constants import OUTPUT_DIR, UPLOADS_DIR
from pymoji.emoji import replace_faces
from pymoji.utils import allowed_file, get_id_name, get_json_name, get_output_name, \
    orient_image, save_to_cloud, write_json


def detect_faces(input_stream=None, input_uri=None):
    """Uses the Vision API to detect faces in an input image. Pass the input
    image as either a BufferedIO stream (takes precedence) or a Google Cloud
    Storage URI.

    https://googlecloudplatform.github.io/google-cloud-python/latest/vision/index.html#annotate-an-image
    https://googlecloudplatform.github.io/google-cloud-python/latest/vision/gapic/v1/types.html#google.cloud.vision_v1.types.Image
    https://googlecloudplatform.github.io/google-cloud-python/latest/vision/gapic/v1/types.html#google.cloud.vision_v1.types.ImageSource
    https://googlecloudplatform.github.io/google-cloud-python/latest/vision/gapic/v1/types.html#google.cloud.vision_v1.types.AnnotateImageRequest
    https://googlecloudplatform.github.io/google-cloud-python/latest/vision/gapic/v1/types.html#google.cloud.vision_v1.types.Feature
    https://googlecloudplatform.github.io/google-cloud-python/latest/vision/gapic/v1/types.html#google.cloud.vision_v1.types.AnnotateImageResponse

    Args:
        input_stream: a BufferedIO stream containing an image with faces.
        input_uri: an image uri for either Google Cloud storage
            e.g. 'gs://bucket_name/path/to/image.jpg'
            or public HTTP/HTTP url
            e.g. 'http://cdn/path/to/image.jpg'

    Returns:
        an array of Face annotation objects found in the input image.
    """
    print('Detecting faces...')
    client = vision.ImageAnnotatorClient()

    # convert input image to Google Cloud Image
    content = None
    source = None
    if input_stream:
        content = input_stream.read()
    elif input_uri:
        source = types.ImageSource(image_uri=input_uri) # pylint: disable=no-member
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


def process_path(input_path):
    """Processes the image at the specified input path and returns the
    ID-filename from the run. This is the CLI entrypoint.

    Args:
        input_path: path to source image file

    Returns:
        an ID-filename string for the run
    """
    filename = os.path.basename(input_path)
    id_filename = None
    if os.path.isfile(input_path) and allowed_file(filename):
        with open(input_path, 'rb') as input_file:
            id_filename = process_local(input_file, filename)
    else:
        print('skipped non-image file')
    return id_filename


def process_local(image_stream, input_filename):
    """Local dev server entrypoint that processes the given image and returns
    the ID-filename from the run. Creates the output directory first if necessary.

    Only used when APP.testing == True.

    Args:
        image_stream: a BufferedIO containing an image
        input_filename: string filename of the source image

    Returns:
        an ID-filename string for the run
    """
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print('created output directory {}'.format(OUTPUT_DIR))

    id_filename = get_id_name(input_filename)
    id_path = os.path.join(UPLOADS_DIR, id_filename)
    print('Saving to file: {}'.format(id_path))
    with open(id_path, 'wb') as id_file:
        orient_image(image_stream, id_file) # rotate based on EXIF

    with open(id_path, 'rb') as id_file:
        faces = detect_faces(input_stream=id_file)
        id_file.seek(0) # reset the file pointer for next use

        if faces:
            json_filename = get_json_name(id_filename)
            json_path = os.path.join(OUTPUT_DIR, json_filename)
            print('Saving to file: {}'.format(json_path))
            with open(json_path, 'w') as json_file:
                write_json(faces, json_file)

            output_filename = get_output_name(id_filename)
            output_path = os.path.join(OUTPUT_DIR, output_filename)
            print('Saving to file: {}'.format(output_path))
            replace_faces(id_file, faces, output_path)

    return id_filename


def process_cloud(image_stream, input_filename, mime):
    """Production server entrypoint that processes the given image and returns
    the ID-filename from the run. Uploads both the input and ouput images to
    Google Cloud Storage.

    Only used when APP.testing == False.

    Uses NamedTemporaryFile to create ephemeral binary streams instead of cruft
    on the webserver file system.

    https://docs.python.org/3/library/tempfile.html#tempfile.NamedTemporaryFile

    Args:
        image_stream: a BufferedIO containing an image
        input_filename: string filename of the source image
        mime: MIME content type string

    Returns:
        an ID-filename string for the run
    """
    id_filename = get_id_name(input_filename)

    # suffix for named temp files so pillow can auto match file encodings
    _, suffix = os.path.splitext(input_filename)
    with NamedTemporaryFile(suffix=suffix) as input_stream:
        orient_image(image_stream, input_stream) # rotate based on EXIF
        input_stream.seek(0) # reset the stream for next use

        save_to_cloud(input_stream, 'uploads/' + id_filename, mime)
        input_stream.seek(0) # reset the stream for next use

        # gs://bucket_name/object_name
        input_uri = "gs://{}/uploads/{}".format(PROJECT_ID, id_filename)
        faces = detect_faces(input_uri=input_uri)

        if faces:
            with NamedTemporaryFile(suffix=suffix, mode='w+') as json_stream:
                write_json(faces, json_stream)
                json_stream.seek(0) # reset the stream for next use

                json_filename = get_json_name(id_filename)
                save_to_cloud(json_stream, 'gen/' + json_filename, 'application/json')

            with NamedTemporaryFile(suffix=suffix) as output_stream:
                replace_faces(input_stream, faces, output_stream)
                output_stream.seek(0) # reset the stream for next use

                output_filename = get_output_name(id_filename)
                save_to_cloud(output_stream, 'gen/' + output_filename, mime)

    return id_filename
