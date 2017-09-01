"""Uses pillow image library and emojione images to manipulate image files.

http://pillow.readthedocs.io/en/4.2.x/reference/Image.html
https://www.emojione.com/emoji/v3
http://unicode.org/emoji/charts/full-emoji-list.html
"""
from tempfile import TemporaryFile

from PIL import Image, ImageDraw

from pymoji import FACE_PAD, USE_BIG_GUNS
from pymoji.constants import EMOJI_CDN_PATH
from pymoji.constants import VERY_UNLIKELY, UNLIKELY, POSSIBLE, LIKELY, VERY_LIKELY
from pymoji.utils import download_image, average_points
from pymoji.vision import detect_labels, to_vision_image


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


def compute_emoji_box(image, face, face_pad=FACE_PAD):
    """Computes a 4-tuple defining the left, upper, right, and lower pixel
    coordinate for the emoji bounding box based on the given image and face
    annotation metadata. Remember that the upper-left corner is the origin!

    Args:
        image: a PIL.Image
        face: a face annotation object from the Google Vision API.
        face_pad: percentage to enlarge emoji beyond face bounding box

    Returns:
        a 4-tuple defining the left, upper, right, and lower pixel coordinate
            e.g. (0, 0, 128, 128)
    """
    face_top_left = face.bounding_poly.vertices[0]
    face_left = face_top_left.x
    face_top = face_top_left.y

    face_bottom_right = face.bounding_poly.vertices[2]
    face_right = face_bottom_right.x
    face_bottom = face_bottom_right.y

    # compute height and width (top-left corner is origin)
    face_height = face_bottom - face_top
    face_width = face_right - face_left

    # compute extra padding to approximate head-size
    width_pad = face_width * face_pad
    height_pad = face_height * face_pad

    # original image bounding box
    (image_left, image_top, image_right, image_bottom) = image.getbbox()

    # add padding, use max and min to limit based on outer image
    left = max(image_left, int(face_left - width_pad))
    top = max(image_top, int(face_top - height_pad))
    right = min(image_right, int(face_right + width_pad))
    bottom = min(image_bottom, int(face_bottom + height_pad))

    return (left, top, right, bottom)


def get_emoji_image(code, box):
    """Creates an emoji RGBA PIL.Image for the given code, scaled to the
    given bounding box. Maintains a cache of original templates (CDN source
    files are 128x128 PNGs).

    Args:
        code: a string containing the code for the desired emoji.
        box: a 4-tuple defining the emoji bounding box (see compute_emoji_box)

    Returns:
        a scaled RGBA PIL.Image of the emoji.
    """
    if code not in EMOJI:
        # handle cache miss
        emoji_url = EMOJI_CDN_PATH + code + '.png'
        emoji = download_image(emoji_url).convert('RGBA')
        EMOJI[code] = emoji

    # compute height and width (top-left corner is origin)
    (left, top, right, bottom) = box
    height = bottom - top
    width = right - left

    # get image from cache and resize
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


def compute_emoji_code(image, face, box, use_big_guns=USE_BIG_GUNS):
    """Computes the 'best' emoji string code for the given face in the given
    image.

    Args:
        image: a PIL.Image
        face: a face annotation object from the Google Vision API.
        box: a 4-tuple defining the emoji bounding box (see compute_emoji_box)
        use_big_guns: whether or not to fallback on label analysis (slow)

    Returns:
        an emoji string code
    """

    # check likelihood scores in roughly inverse-frequency order
    # i.e. ensure that rare sorrow emoji outrank common joy emoji
    if face.sorrow_likelihood > VERY_UNLIKELY:
        return get_code(face.sorrow_likelihood, SORROW_CODES)
    elif face.anger_likelihood > VERY_UNLIKELY:
        return get_code(face.anger_likelihood, ANGER_CODES)
    elif face.surprise_likelihood > VERY_UNLIKELY:
        return get_code(face.surprise_likelihood, SURPRISE_CODES)
    elif face.headwear_likelihood > POSSIBLE:
        return "1f920" # cowboy hat face
    elif face.joy_likelihood > VERY_UNLIKELY:
        return get_code(face.joy_likelihood, JOY_CODES)
    elif use_big_guns:
        # BRING OUT THE BIG GUNS - analyze labels on individual head

        # crop head + save into temp file
        head_image = image.crop(box)
        with TemporaryFile() as head_stream:
            head_image.save(head_stream, format='JPEG')
            head_stream.seek(0)

            # submit head image for labels
            gv_head_image = to_vision_image(input_stream=head_stream)
            labels = detect_labels(gv_head_image)

            # greedily convert first interesting label into emoji
            for label in labels:
                if label.description == "sunglasses": # at night so I can so I caaaaan
                    return "1f60e" # smiling face with sunglasses
                elif label.description == "glasses":
                    return "1f913" # nerd face

    return DEFAULT_CODE


def render_emoji(image, face):
    """Renders an emoji on top of the given image using the given face
    annotation data.

    https://googlecloudplatform.github.io/google-cloud-python/latest/vision/gapic/v1/types.html#google.cloud.vision_v1.types.AnnotateImageResponse

    Args:
        image: a PIL.Image
        face: a face annotation object from the Google Vision API.
    """
    emoji_box = compute_emoji_box(image, face)
    emoji_code = compute_emoji_code(image, face, emoji_box)

    #bring back some rectangularness as a function of height

    emoji_size = height # for now, this is pretty much always largest

    midpoint_between_eyes = face.landmarks[6].position
    nose_tip = face.landmarks[7].position

    center_of_emoji = average_points(midpoint_between_eyes, nose_tip)

    top_left.x = int(center_of_emoji['x'] - emoji_size/2)
    top_left.y = int(center_of_emoji['y'] - emoji_size/2)

    """
    Hat emoji yellow face is smaller than normal yellow face and should be
    113% wider and 112% taller to get the same ammount of yellow face.
    """
    if emoji_code == "1f920":
        # calc scaled up size
        hat_avg = emoji_size * 1.16
        # calc new top left corner, transformed from center bottom
        top_left.y -= int(hat_avg - emoji_size) # entirety of the new tallness
        top_left.x -= int((hat_avg - emoji_size)/2) # half of the new fatness

        # set new sizes
        emoji_size = int(hat_avg)

    emoji = get_emoji_image(emoji_code, emoji_box)
    image.paste(emoji, emoji_box, emoji)


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


def highlight_faces(input_stream, faces, output_stream):
    """Draws a bounding box around all faces in the given input image based on
    the given face annotation data, then writes to the given output.

    The input and output may be either a filename (string), pathlib.Path object,
    or BufferedIO stream with read and write access, respectively.

    Args:
        input_stream: a file-like-object containing an image.
        faces: a list of face annotation objects from the Google Vision API.
        output_stream: a file-like-object to write the result to.
    """
    output_image = Image.open(input_stream)
    draw = ImageDraw.Draw(output_image)
    for face in faces:
        box = [(vertex.x, vertex.y)
               for vertex in face.bounding_poly.vertices]
        draw.line(box + [box[0]], width=5, fill='#00ff00')
    output_image.save(output_stream)
    output_image.close()
