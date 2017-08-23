"""Replaces detected faces in the given image with emoji."""
import os
from tempfile import NamedTemporaryFile

from google.cloud import vision
from google.cloud.vision import types

from pymoji.constants import MAX_RESULTS, OUTPUT_DIR, PROJECT_ID, UPLOADS_DIR
from pymoji.emoji import replace_faces
from pymoji.utils import allowed_file, get_id_name, get_output_name, orient_image, save_to_cloud


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
    return id_filename


def process_local(image, input_filename):
    """Local dev server entrypoint that processes the given image and returns
    the ID-filename from the run. Creates the output directory first if necessary.

    Only used when APP.testing == True.

    Args:
        image: an image file-object
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
    with open(id_path, 'wb') as input_file:
        orient_image(image, input_file) # rotate based on EXIF

    with open(id_path, 'rb') as input_file:
        faces = detect_faces(input_content=input_file)
        input_file.seek(0) # Reset the file pointer, so we can read the file again

        if faces:
            output_filename = get_output_name(id_filename)
            output_path = os.path.join(OUTPUT_DIR, output_filename)
            print('Saving to file: {}'.format(output_path))
            replace_faces(input_file, faces, output_path)

    return id_filename


def process_cloud(image, input_filename, mime):
    """Production server entrypoint that processes the given image and returns
    the ID-filename from the run. Uploads both the input and ouput images to
    Google Cloud Storage.

    Only used when APP.testing == False.

    Args:
        image: an image file-object
        input_filename: string filename of the source image
        mime: MIME content type string

    Returns:
        an ID-filename string for the run
    """
    id_filename = get_id_name(input_filename)

    # suffix for named temp files so pillow can auto match file encodings
    suffix = '.' + input_filename.rsplit('.', 1)[1]
    with NamedTemporaryFile(suffix=suffix) as input_file:
        orient_image(image, input_file) # rotate based on EXIF
        input_file.seek(0) # Reset the file pointer, so we can read the file again

        save_to_cloud(input_file, 'uploads/' + id_filename, mime)
        input_file.seek(0) # Reset the file pointer, so we can read the file again

        # gs://bucket_name/object_name
        input_source = "gs://{}/uploads/{}".format(PROJECT_ID, id_filename)
        faces = detect_faces(input_source=input_source)

        if faces:
            with NamedTemporaryFile(suffix=suffix) as output_file:
                replace_faces(input_file, faces, output_file)
                output_file.seek(0) # Reset the file pointer, so we can read the file again

                output_filename = get_output_name(id_filename)
                save_to_cloud(output_file, 'gen/' + output_filename, mime)

    return id_filename
