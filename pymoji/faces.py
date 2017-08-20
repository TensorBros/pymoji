"""Replaces detected faces in the given image with emoji."""
import os

from google.cloud import vision
from google.cloud.vision import types
from PIL import Image

from pymoji.constants import EMOJI_DIR, LIKELY, MAX_RESULTS, OUTPUT_DIR, UNLIKELY, VERY_UNLIKELY


def detect_face(input_content=None, input_source=None):
    """Uses the Vision API to detect faces in an input image. Pass the input
    image as a binary stream (takes precedence), Google Cloud source URI,
    or both.

    https://googlecloudplatform.github.io/google-cloud-python/latest/vision/index.html#annotate-an-image
    https://googlecloudplatform.github.io/google-cloud-python/latest/vision/gapic/v1/types.html#google.cloud.vision_v1.types.Image
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
        An array of Face objects with information about the picture.
    """
    client = vision.ImageAnnotatorClient()

    # convert input image to Google Cloud Image
    content = None
    source = None
    if input_content:
        content = input_content.read()
    elif input_source:
        source = input_source
    image = types.Image(content=content, source=source) # pylint: disable=no-member

    features = [{
        'type': vision.enums.Feature.Type.FACE_DETECTION,
        'max_results': MAX_RESULTS
    }]
    return client.annotate_image({
        'image': image,
        'features': features
        }).face_annotations # pylint: disable=no-member


def replace_faces(image, faces, output_filename):
    """Replaces all faces with emoji, then saves to output_filename.

    Args:
        image: a file containing the image with the faces.
        faces: a list of faces found in the file. This should be in the format
            returned by the Vision API.
        output_filename: the name of the image file to be created, where the
            faces have polygons drawn around them.
    """
    im = Image.open(image)

    for face in faces:
        render_emoji(im, face)

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    im.save(output_filename)


def open_emoji(code):
    """Generates a PIL.Image from the specified emoji code.
    All image files are 128x128 .pngs from https://www.emojione.com/emoji/v3

    Args:
        code: a string containing the code for the desired emoji.

    Returns:
        a PIL.Image of the emoji.
    """
    path = os.path.join(EMOJI_DIR, code + ".png")
    return Image.open(path).convert('RGBA')


def render_emoji(image, face):
    """Hacky helper method to start exposing sentiment likelihood scores.

    Args:
        image: a PIL.Image
        face: a face object in the format returned by the Vision API.
    """

    # default face that everyone starts with:
    emoji_code = "1f642"

    # extras:
    # basic_smile_code = "1f642"
    # roseycheeks_code = "1f60a"
    # expressionless_face_code = "1f610"
    # confused_code = "1f615"
    # tears_code = "1f602"

    # basic sentiment emoji
    sorrow_emoji_code = "1f622"
    anger_emoji_code = "1f620"
    surprise_emoji_code = "1f632"
    joy_1_emoji_code = "1f601"
    joy_2_emoji_code = "1f604"
    joy_3_emoji_code = "1f606"

    # super crude sentiment logic
    if face.sorrow_likelihood > VERY_UNLIKELY:
        emoji_code = sorrow_emoji_code
    elif face.anger_likelihood > VERY_UNLIKELY:
        emoji_code = anger_emoji_code
    elif face.surprise_likelihood > VERY_UNLIKELY:
        emoji_code = surprise_emoji_code
    elif face.joy_likelihood > LIKELY:
        emoji_code = joy_3_emoji_code
    elif face.joy_likelihood > UNLIKELY:
        emoji_code = joy_2_emoji_code
    elif face.joy_likelihood > VERY_UNLIKELY:
        emoji_code = joy_1_emoji_code

    # scale and render emoji over bounding box
    top_left = face.bounding_poly.vertices[0]
    bottom_right = face.bounding_poly.vertices[2]
    width = (bottom_right.x - top_left.x)
    height = (bottom_right.y - top_left.y)
    emoji = open_emoji(emoji_code).resize((width, height), resample=0)
    image.paste(emoji, (top_left.x, top_left.y), emoji)


def main(input_filename, output_filename):
    with open(input_filename, 'rb') as image:
        faces = detect_face(image)
        print('Found {} face{}'.format(
            len(faces), '' if len(faces) == 1 else 's'))
        if len(faces) > 0:
            print('Writing to file {}'.format(output_filename))
            # Reset the file pointer, so we can read the file again
            image.seek(0)
            replace_faces(image, faces, output_filename)
