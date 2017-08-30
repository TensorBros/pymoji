"""Uses pillow image library and emojione images to manipulate image files.

http://pillow.readthedocs.io/en/4.2.x/reference/Image.html
https://www.emojione.com/emoji/v3
http://unicode.org/emoji/charts/full-emoji-list.html
"""
from tempfile import TemporaryFile

from PIL import Image

from pymoji.constants import EMOJI_CDN_PATH
from pymoji.constants import VERY_UNLIKELY, UNLIKELY, POSSIBLE, LIKELY, VERY_LIKELY
from pymoji.utils import download_image
from pymoji.vision import detect_labels


# dictionary object to use as in-memory cache of emoji images
# key: emoji code string
# value: 128x128 RGBA PIL.Image
EMOJI = {} # cache

DEFAULT_CODE = "1f642" # slightly smiling face
SORROW_CODES = [
    "1f641", # slightly frowning face
    #"2639", # frowning face
    "1f61f", # worried face
    "1f61e", # disappointed face
    "1f622", # crying face
    # "1f62d", # loudly crying face
]
ANGER_CODES = [
    "1f610", # neutral face
    "1f610", # neutral face
    "1f620", # angry face
    "1f620", # angry face
    # "1f621", # pouting face
    # "1f624", # face with steam from nose
    # "1f92c", # face with symbols over mouth
]
SURPRISE_CODES = [
    "1f62f", # hushed face
    "1f62e", # face with open mouth
    # "1f627", # anguished face
    "1f632", # astonished face
    "1f628", # fearful face
    # "1f631", # face screaming in fear
]
JOY_CODES = [
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
# MISC CODES
# "1f615" # confused face
# "1f913" # nerd face
# "1f60e" # smiling face with sunglasses
# "1f61b" # face with stuck-out tongue
# "1f60d" # smiling face with heart-eyes
# "1f644" # face with rolling eyes


def get_emoji(code, width, height):
    """Returns the emoji for the given emoji code as a RGBA PIL.Image scaled
    to the given width and height. Maintains a cache of original templates
    (CDN source files are 128x128 PNGs).

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


def get_code(likelihood, code_list):
    """Returns a code from the given list based on the given likelihood. Super basic.

    https://cloud.google.com/vision/docs/reference/rest/v1/images/annotate#likelihood

    Args:
        likelihood: an integer representing google vision likelihood
        code_list: a list containing exactly 4 emoji codes in ascending order

    Returns:
        an emoji string code
    """
    if likelihood == VERY_LIKELY:
        return code_list[3]
    elif likelihood == LIKELY:
        return code_list[2]
    elif likelihood == POSSIBLE:
        return code_list[1]
    elif likelihood == UNLIKELY:
        return code_list[0]
    return DEFAULT_CODE


def render_emoji(image, face):
    """Renders an emoji on top of the given image using the given face
    annotation data.

    https://googlecloudplatform.github.io/google-cloud-python/latest/vision/gapic/v1/types.html#google.cloud.vision_v1.types.AnnotateImageResponse

    Args:
        image: a PIL.Image
        face: a face annotation object from the Google Vision API.
    """
    top_left = face.bounding_poly.vertices[0]
    bottom_right = face.bounding_poly.vertices[2]
    width = (bottom_right.x - top_left.x)
    height = (bottom_right.y - top_left.y)
    emoji_code = DEFAULT_CODE

    # check likelihood scores in roughly inverse-frequency order
    # i.e. ensure that rare sorrow emoji outrank common joy emoji
    if face.sorrow_likelihood > VERY_UNLIKELY:
        emoji_code = get_code(face.sorrow_likelihood, SORROW_CODES)
    elif face.anger_likelihood > VERY_UNLIKELY:
        emoji_code = get_code(face.anger_likelihood, ANGER_CODES)
    elif face.surprise_likelihood > VERY_UNLIKELY:
        emoji_code = get_code(face.surprise_likelihood, SURPRISE_CODES)
    elif face.headwear_likelihood > POSSIBLE:
        emoji_code = "1f920" # cowboy hat face
    elif face.joy_likelihood > VERY_UNLIKELY:
        emoji_code = get_code(face.joy_likelihood, JOY_CODES)
    else:
        # BRING OUT THE BIG GUNS - analyze labels on individual face

        # compute padding and face crop box
        width_pad = width * 0.1
        height_pad = height * 0.1
        # use max and min to limit padding based on outer image
        image_box = image.getbbox()
        face_box = (
            max(image_box[0], top_left.x - width_pad),
            max(image_box[1], top_left.y - height_pad),
            min(image_box[2], bottom_right.x + width_pad),
            min(image_box[3], bottom_right.y + height_pad)
        )

        # crop face + save into temp file
        face_image = image.crop(face_box)
        with TemporaryFile() as face_stream:
            face_image.save(face_stream, format='JPEG')
            face_stream.seek(0)

            # submit face image for labels
            labels = detect_labels(input_stream=face_stream)

            # greedily convert first interesting label into emoji
            for label in labels:
                if label.description == "sunglasses": # at night so I can so I caaaaan
                    emoji_code = "1f60e" # smiling face with sunglasses
                    continue
                elif label.description == "glasses":
                    emoji_code = "1f913" # nerd face
                    continue

    # scale and render emoji over bounding box
    emoji = get_emoji(emoji_code, width, height)
    image.paste(emoji, (top_left.x, top_left.y), emoji)


def replace_faces(input_stream, faces, output_stream):
    """Replaces all faces in the given input image with emoji based on the
    given face annotation data, then writes to the given output.

    The input and output may be either a filename (string), pathlib.Path object,
    or BufferedIO stream with read and write access, respectively.

    Args:
        input_stream: a file-like-object containing an image.
        faces: a list of face annotation objects from the Google Vision API.
        output_stream: a file-like-object to write the result to.
    """
    output_image = Image.open(input_stream)
    for face in faces:
        render_emoji(output_image, face)
    output_image.save(output_stream)
    output_image.close()
