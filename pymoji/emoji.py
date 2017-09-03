"""Uses pillow image library and emojione images to manipulate image files.

http://pillow.readthedocs.io/en/4.2.x/reference/Image.html
https://www.emojione.com/emoji/v3
http://unicode.org/emoji/charts/full-emoji-list.html
"""
from tempfile import TemporaryFile

from PIL import Image, ImageDraw

from pymoji import FACE_PAD, USE_BIG_GUNS
from pymoji.constants import EMOJI_CDN_PATH
from pymoji.constants import UNLIKELY, POSSIBLE, LIKELY, VERY_LIKELY
from pymoji.utils import download_image, average_points
from pymoji.vision import detect_labels, to_vision_image


# dictionary object to use as in-memory cache of emoji images
# key: emoji code string
# value: 128x128 RGBA PIL.Image
EMOJI = {} # cache

DEFAULT_CODE = "1f642" # slightly smiling face

SORROW_MAP = {
    UNLIKELY: "1f641", # slightly frowning face
    #"2639", # frowning face
    POSSIBLE: "1f61f", # worried face
    LIKELY: "1f61e", # disappointed face
    VERY_LIKELY: "1f622", # crying face
    # "1f62d", # loudly crying face
}

ANGER_MAP = {
    UNLIKELY: "1f610", # neutral face
    POSSIBLE: "1f610", # neutral face
    LIKELY: "1f620", # angry face
    VERY_LIKELY: "1f620", # angry face
    # "1f621", # pouting face
    # "1f624", # face with steam from nose
    # "1f92c", # face with symbols over mouth
}

SURPRISE_MAP = {
    UNLIKELY: "1f62f", # hushed face
    POSSIBLE: "1f62e", # face with open mouth
    # "1f627", # anguished face
    LIKELY: "1f632", # astonished face
    VERY_LIKELY: "1f628", # fearful face
    # "1f631", # face screaming in fear
}

JOY_MAP = {
    # "1f642", # slightly smiling face
    UNLIKELY: "1f60c", # relieved face
    # "263a", # smiling face
    # "1f60a", # smiling face with smiling eyes & rosy cheeks
    # "1f600", # grinning face
    POSSIBLE: "1f603", # smiling face with open mouth
    LIKELY: "1f601", # grinning face with smiling eyes
    # "1f604", # smiling face with open mouth & smiling eyes
    VERY_LIKELY: "1f606", # smiling face with open mouth & closed eyes
    # "1f602", # face with tears of joy
    # "1f923", # rolling on the floor laughing
}

# earlier in list ~ funnier / rarer
HUMOR_RANK = [
    # sorrow likelihood
    "1f622", # crying face
    "1f61e", # disappointed face
    "1f61f", # worried face
    "1f641", # slightly frowning face

    # anger likelihood
    "1f620", # angry face
    "1f610", # neutral face

    # surprise likelihood
    "1f628", # fearful face
    "1f632", # astonished face
    "1f62e", # face with open mouth
    "1f62f", # hushed face

    # joy likelihood - rare
    "1f606", # smiling face with open mouth & closed eyes
    "1f601", # grinning face with smiling eyes

    # headwear likelihood
    "1f920", # cowboy hat face

    # big guns
    "1f60e", # smiling face with sunglasses
    "1f913", # nerd face

    # joy likelihood - boring
    "1f603", # smiling face with open mouth
    "1f60c", # relieved face

    # default
    "1f642", # slightly smiling face

    # currently impossible, but someday...
    "1f615", # confused face
    "1f61b", # face with stuck-out tongue
    "1f60d", # smiling face with heart-eyes
    "1f644", # face with rolling eyes
]


def get_humor_rank(code):
    """Computes a humor ranking value for the given emoji code. A lower rank
    roughly means a funnier or rarer emoji.

    Args:
        code: a string containing an emoji code

    Returns:
        an integer humor rank, lower is better
    """
    return HUMOR_RANK.index(code)


def get_face_box(face):
    """Returns a 4-tuple defining the left, upper, right, and lower pixel
    coordinate for the bounding box of the given face annotation metadata.
    Remember that the upper-left corner is the origin!

    Args:
        face: a face annotation object from the Google Vision API.

    Returns:
        a 4-tuple defining the left, upper, right, and lower pixel of the face
        bounding-box
    """
    face_top_left = face.bounding_poly.vertices[0]
    face_left = face_top_left.x
    face_top = face_top_left.y

    face_bottom_right = face.bounding_poly.vertices[2]
    face_right = face_bottom_right.x
    face_bottom = face_bottom_right.y

    return (face_left, face_top, face_right, face_bottom)


def get_depth_rank(face):
    """Computes a ranking value for the given face annotation metadata object.
    Initially based on a super crude approximation of depth.

    Depth approximation: humans are highly unlikely to be hanging-upside down,
        therefore a taller face is further away, break ties with area

    Note: initial tests using area as a proxy for depth yielded unstable results.

    Args:
        face: a face annotation object from the Google Vision API.

    Returns:
        a float value roughly approximating depth
    """
    (_face_left, face_top, _face_right, _face_bottom) = get_face_box(face)
    return face_top


def get_emoji_box(face, face_pad=FACE_PAD, code=None):
    """Computes a 4-tuple defining the left, upper, right, and lower pixel
    coordinate for the emoji bounding box based on the given face
    annotation metadata. Remember that the upper-left corner is the origin!

    Args:
        face: a face annotation object from the Google Vision API.
        face_pad: percentage to enlarge emoji beyond face bounding box

    Returns:
        a 4-tuple defining the left, upper, right, and lower pixel coordinate
            e.g. (0, 0, 128, 128)
    """
    (face_left, face_top, face_right, face_bottom) = get_face_box(face)

    # compute height and width (top-left corner is origin)
    face_height = face_bottom - face_top
    face_width = face_right - face_left

    # find center of emoji
    face_top_left = face.bounding_poly.vertices[0]
    face_bottom_right = face.bounding_poly.vertices[2]
    center_of_emoji = average_points(face_top_left, face_bottom_right)

    # for now, always use square emoji
    # TODO bring back some rectangularness as a function of height?
    emoji_size = int(max(face_height, face_width) * (1 + face_pad))

    # TODO experiment with face landmarks to adjust position
    # midpoint_between_eyes = face.landmarks[6].position
    # nose_tip = face.landmarks[7].position
    # center_of_emoji = average_points(midpoint_between_eyes, nose_tip)

    # scale and render emoji over bounding box
    left = int(center_of_emoji['x'] - emoji_size / 2)
    top = int(center_of_emoji['y'] - emoji_size / 2)

    if code == "1f920": # cowboy hat face
        """
        Hat emoji yellow face is smaller than normal yellow face and should be
        113% wider and 112% taller to get the same ammount of yellow face.
        """
        # calc scaled up size
        hat_avg = emoji_size * 1.16

        # calc new top left corner, transformed from center bottom
        top -= int(hat_avg - emoji_size) # entirety of the new tallness
        left -= int((hat_avg - emoji_size) / 2) # half of the new fatness

        # set new sizes
        emoji_size = int(hat_avg)

    right = left + emoji_size
    bottom = top + emoji_size

    return (left, top, right, bottom)


def get_emoji_image(code, box):
    """Creates an emoji RGBA PIL.Image for the given code, scaled to the
    given bounding box. Maintains a cache of original templates (CDN source
    files are 128x128 PNGs).

    Args:
        code: a string containing the code for the desired emoji.
        box: a 4-tuple defining the emoji bounding box (see get_emoji_box)

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


def get_emoji_code(image, face, use_big_guns=USE_BIG_GUNS):
    """Computes the 'best' emoji string code for the given face in the given
    image.

    Args:
        image: the original PIL.Image containing the face
        face: a face annotation object from the Google Vision API.
        use_big_guns: whether or not to fallback on label analysis (slow)

    Returns:
        an emoji string code
    """
    sorrow_code = SORROW_MAP.get(face.sorrow_likelihood, DEFAULT_CODE)
    anger_code = ANGER_MAP.get(face.anger_likelihood, DEFAULT_CODE)
    surprise_code = SURPRISE_MAP.get(face.surprise_likelihood, DEFAULT_CODE)
    joy_code = JOY_MAP.get(face.joy_likelihood, DEFAULT_CODE)

    candidates = set([sorrow_code, anger_code, surprise_code, joy_code])

    if face.headwear_likelihood > POSSIBLE:
        candidates.add("1f920") # cowboy hat face

    if len(candidates) == 1 and use_big_guns:
        # BRING OUT THE BIG GUNS - analyze labels on individual head

        # crop head + save into temp file
        head_box = get_emoji_box(face)
        head_image = image.crop(head_box)
        with TemporaryFile() as head_stream:
            head_image.save(head_stream, format='JPEG')
            head_stream.seek(0)

            # submit head image for labels
            gv_head_image = to_vision_image(input_stream=head_stream)
            labels = detect_labels(gv_head_image)

            # greedily convert first interesting label into emoji, then stop
            for label in labels:
                if label.description == "sunglasses": # at night so I can so I caaaaan
                    candidates.add("1f60e") # smiling face with sunglasses
                    break
                elif label.description == "glasses":
                    candidates.add("1f913") # nerd face
                    break

    # sort by humor rank and return the funniest
    ranked_candidates = sorted(candidates, key=get_humor_rank)
    return ranked_candidates[0]


def render_emoji(image, face):
    """Renders an emoji on top of the given image using the given face
    annotation data.

    https://googlecloudplatform.github.io/google-cloud-python/latest/vision/gapic/v1/types.html#google.cloud.vision_v1.types.AnnotateImageResponse

    Args:
        image: a PIL.Image
        face: a face annotation object from the Google Vision API.
    """
    code = get_emoji_code(image, face)
    box = get_emoji_box(face, code=code)
    emoji = get_emoji_image(code, box)
    mask = emoji
    image.paste(emoji, box, mask)


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
    faces_by_depth = sorted(faces, key=get_depth_rank)

    for face in faces_by_depth:
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
