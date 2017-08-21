"""Replaces detected faces in the given image with emoji."""
from io import BytesIO
import os
import requests

from flask import url_for
from google.cloud import vision
from google.cloud.vision import types
from PIL import Image

from pymoji.constants import EMOJI_CDN_PATH, MAX_RESULTS, OUTPUT_DIR
from pymoji.constants import VERY_UNLIKELY, UNLIKELY, POSSIBLE, LIKELY, VERY_LIKELY

from pymoji.utils import save_to_cloud


def download_image(image_uri):
    """Downloads the image at the given URI and returns it as a PIL.Image.

    http://pillow.readthedocs.io/en/4.2.x/reference/Image.html

    Args:
        image_uri: an image uri, e.g. 'http://cdn/path/to/image.jpg'

    Returns:
        a PIL.Image of awesomeness
    """
    print('Downloading source image: {} ...'.format(image_uri))
    response = requests.get(image_uri)
    print('...download completed.')
    return Image.open(BytesIO(response.content))


def to_image(input_content=None, input_source=None):
    """Standardizes an input image. Pass the input as a binary stream (takes
    precedence), Google Cloud source URI, or both.

    https://googlecloudplatform.github.io/google-cloud-python/latest/vision/gapic/v1/types.html#google.cloud.vision_v1.types.Image
    https://googlecloudplatform.github.io/google-cloud-python/latest/vision/gapic/v1/types.html#google.cloud.vision_v1.types.ImageSource

    Args:
        input_content: a binary stream containing an image with faces.
        input_source: an image uri for either Google Cloud storage
            e.g. 'gs://bucket_name/path/to/image.jpg'
            or public http/https url
            e.g. 'http://cdn/path/to/image.jpg'

    Returns:
        a google vision image object
    """
    content = None
    source = None
    if input_content:
        content = input_content.read()
    elif input_source:
        source = types.ImageSource(image_uri=input_source) # pylint: disable=no-member
    return types.Image(content=content, source=source) # pylint: disable=no-member


def detect_faces(input_content=None, input_source=None):
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
    image = to_image(input_content=input_content, input_source=input_source)
    print('Detecting faces...')

    features = [{
        'type': vision.enums.Feature.Type.FACE_DETECTION,
        'max_results': MAX_RESULTS
    }]
    faces = client.annotate_image({
        'image': image,
        'features': features
        }).face_annotations # pylint: disable=no-member
    print('...found {} face{}.'.format(len(faces), '' if len(faces) == 1 else 's'))
    return faces


def replace_faces(faces, input_content=None, input_source=None):
    """Replaces all given faces in the given image with emoji and returns the
    resulting image. Pass the input image as a binary stream (takes precedence),
    Google Cloud source URI, or both.

    http://pillow.readthedocs.io/en/4.2.x/reference/Image.html

    Args:
        faces: a list of faces detected in the image. This should be in the
            format returned by the Google Cloud Vision API.
        input_content: a binary stream containing an image with faces.
        input_source: an image uri for either Google Cloud storage
            e.g. 'gs://bucket_name/path/to/image.jpg'
            or public http/https url
            e.g. 'http://cdn/path/to/image.jpg'

    Returns:
        a PIL.Image of awesomeness
    """
    if input_content:
        output_image = Image.open(input_content)
    elif input_source:
        output_image = download_image(input_source)

    for face in faces:
        render_emoji(output_image, face)

    return output_image


EMOJI = {} # cache

def get_emoji(code, width, height):
    """Returns the emoji for the given emoji code as a RGBA PIL.Image scaled
    to the given width and height. Maintains a cache of original templates.

    Original emoji image files are 128x128 PNGs from https://www.emojione.com/emoji/v3

    Args:
        code: a string containing the code for the desired emoji.

    Returns:
        a scaled RGBA PIL.Image of the emoji.
    """
    if code not in EMOJI:
        # handle cache miss
        emoji_url = EMOJI_CDN_PATH + code + '.png'
        emoji = download_image(emoji_url).convert('RGBA')
        EMOJI[code] = emoji
    return EMOJI[code].resize((width, height), resample=0)


def render_emoji(image, face):
    """Hacky helper method to start exposing sentiment likelihood scores.

    Args:
        image: a PIL.Image
        face: a face object in the format returned by the Vision API.
    """
    sorrow_emoji = [
        "1f641", # slightly frowning face
        #"2639", # frowning face
        "1f61f", # worried face
        "1f61e", # disappointed face
        "1f622", # crying face
        # "1f62d", # loudly crying face
    ]
    anger_emoji = [
        "1f610", # neutral face
        "1f610", # neutral face
        "1f620", # angry face
        "1f620", # angry face
        # "1f621", # pouting face
        # "1f624", # face with steam from nose
        # "1f92c", # face with symbols over mouth
    ]
    surprise_emoji = [
        "1f62f", # hushed face
        "1f62e", # face with open mouth
        # "1f627", # anguished face
        "1f632", # astonished face
        "1f628", # fearful face
        # "1f631", # face screaming in fear
    ]
    joy_emoji = [
        # "1f642", # slightly smiling face
        "1f60c", # relieved face
        # "263a", # smiling face
        # "1f60a", # smiling face with smiling eyes & rosy cheeks
        # "1f600", # grinning face
        "1f603", # smiling face with open mouth
        "1f601", # grinning face with smiling eyes
        # "1f604", # smiling face with open mouth & smiling eyes
        "1f606", # smiling face with open mouth & closed eyes
        # "1f602", # face with tears of joy
        # "1f923", # rolling on the floor laughing
    ]
    # MISC
    # "1f615" # confused face
    # "1f913" # nerd face
    # "1f60e" # smiling face with sunglasses
    # "1f61b" # face with stuck-out tongue
    # "1f60d" # smiling face with heart-eyes
    # "1f644" # face with rolling eyes

    def get_code(likelihood, code_list):
        """assumes code_list has exactly 4 codes in ascending order"""
        if likelihood == VERY_LIKELY:
            return code_list[3]
        elif likelihood == LIKELY:
            return code_list[2]
        elif likelihood == POSSIBLE:
            return code_list[1]
        elif likelihood == UNLIKELY:
            return code_list[0]
        return "1f642" # slightly smiling face

    # default face that everyone starts with:
    emoji_code = "1f642" # slightly smiling face

    # check likelihood scores in roughly inverse-frequency order
    # i.e. ensure that rare sorrow emoji outrank common joy emoji
    if face.sorrow_likelihood > VERY_UNLIKELY:
        emoji_code = get_code(face.sorrow_likelihood, sorrow_emoji)
    elif face.anger_likelihood > VERY_UNLIKELY:
        emoji_code = get_code(face.anger_likelihood, anger_emoji)
    elif face.surprise_likelihood > VERY_UNLIKELY:
        emoji_code = get_code(face.surprise_likelihood, surprise_emoji)
    elif face.headwear_likelihood > POSSIBLE:
        emoji_code = "1f920" # cowboy hat face
    elif face.joy_likelihood > VERY_UNLIKELY:
        emoji_code = get_code(face.joy_likelihood, joy_emoji)

    # scale and render emoji over bounding box
    top_left = face.bounding_poly.vertices[0]
    bottom_right = face.bounding_poly.vertices[2]
    width = (bottom_right.x - top_left.x)
    height = (bottom_right.y - top_left.y)
    emoji = get_emoji(emoji_code, width, height)
    image.paste(emoji, (top_left.x, top_left.y), emoji)


def main(input_path, output_path):
    """Processes the image at the specified input path and writes the
    result to the specified output path. CLI entrypoint.

    Args:
        input_path: path to source image file
        output_path: path to destination image file
    """
    with open(input_path, 'rb') as input_image:
        faces = detect_faces(input_content=input_image)

        if faces:
            input_image.seek(0) # Reset the file pointer, so we can read the file again
            output_image = replace_faces(faces, input_content=input_image)

            print('Saving to file: {}'.format(output_path))
            if not os.path.exists(OUTPUT_DIR):
                os.makedirs(OUTPUT_DIR)
            output_image.save(output_path)


def process_local(image, input_filename, output_filename, local_output_path):
    """Entrypoint called by local dev server when APP.testing == True."""
    local_input_path = os.path.join(OUTPUT_DIR, input_filename)
    image.save(local_input_path)
    image.close()
    input_image_url = url_for('static', filename='gen/' + input_filename)
    main(local_input_path, local_output_path)
    output_image_url = url_for('static', filename='gen/' + output_filename)
    return (input_image_url, output_image_url)


def process_cloud(image, input_filename, output_filename, local_output_path):
    """Google Cloud Storage based entrypoint called by server when
    APP.testing == False."""
    input_image_url = save_to_cloud(image, input_filename, image.content_type)
    output_image_url = input_image_url
    faces = detect_faces(input_source=input_image_url)
    if faces:
        image.seek(0) # Reset the file pointer, so we can read the file again
        output_image = replace_faces(faces, input_content=image)
        # export image and upload result
        output_image.save(local_output_path)
        with open(local_output_path, 'rb') as output_image:
            output_image_url = save_to_cloud(output_image, output_filename,
                image.content_type)
        os.remove(local_output_path) # clean up cruft on webserver
    return (input_image_url, output_image_url)
