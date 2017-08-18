#!/usr/bin/env python

# Copyright 2015 Google, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Draws squares around detected faces in the given image."""

import argparse
import os

# [START import_client_library]
from google.cloud import vision
# [END import_client_library]
from google.cloud.vision import types
from PIL import Image, ImageDraw

from pymoji.app import RESOURCES

EMOJI_DIR = os.path.join(RESOURCES, 'emoji')


# [START def_detect_face]
def detect_face(face_file):
    """Uses the Vision API to detect faces in the given file.

    Args:
        face_file: A file-like object containing an image with faces.

    Returns:
        An array of Face objects with information about the picture.
    """
    # [START get_vision_service]
    client = vision.ImageAnnotatorClient()
    # [END get_vision_service]

    content = face_file.read()
    image = types.Image(content=content)

    return client.face_detection(image=image).face_annotations
# [END def_detect_face]


# [START def_highlight_faces]
def highlight_faces(image, faces, output_filename):
    """Draws a polygon around the faces, then saves to output_filename.

    Args:
      image: a file containing the image with the faces.
      faces: a list of faces found in the file. This should be in the format
          returned by the Vision API.
      output_filename: the name of the image file to be created, where the
          faces have polygons drawn around them.
    """
    im = Image.open(image)
    draw = ImageDraw.Draw(im)

    for face in faces:
        box = [(vertex.x, vertex.y)
               for vertex in face.bounding_poly.vertices]
        # Turn off bounding box for now
        #draw.line(box + [box[0]], width=5, fill='#00ff00')
        render_emoji(im, face)

    im.save(output_filename)
# [END def_highlight_faces]


def open_emoji(code):
    path = os.path.join(EMOJI_DIR, code + ".png")
    return Image.open(path)


def render_emoji(image, face):
    """Hacky helper method to start exposing sentiment likelihood scores.

    Args:
      image: a PIL.Image
      face: a face object in the format returned by the Vision API.
    """

    # default face that everyone starts with:
    emoji = open_emoji("1f642")

    # all faces are 128x128 .pngs from https://www.emojione.com/emoji/v3

    # extras:
    # basic_smile = open_emoji("1f642")
    # roseycheeks = open_emoji("1f60a")
    # expressionless_face = open_emoji("1f610")
    # confused = open_emoji("1f615")
    # tears = open_emoji("1f602")

    # basic sentiment emoji
    sorrow_emoji = open_emoji("1f622")
    anger_emoji = open_emoji("1f620")
    surprise_emoji = open_emoji("1f632")
    joy_1_emoji = open_emoji("1f601")
    joy_2_emoji = open_emoji("1f604")
    joy_3_emoji = open_emoji("1f606")

    # super crude sentiment logic
    if face.sorrow_likelihood > 1:
        emoji = sorrow_emoji
    elif face.anger_likelihood > 1:
        emoji = anger_emoji
    elif face.surprise_likelihood > 1:
        emoji = surprise_emoji
    elif face.joy_likelihood > 4:
        emoji = joy_3_emoji
    elif face.joy_likelihood > 2:
        emoji = joy_2_emoji
    elif face.joy_likelihood > 1:
        emoji = joy_1_emoji

    # hackily render emoji in center of bounding box
    top_left = face.bounding_poly.vertices[0]
    bottom_right = face.bounding_poly.vertices[2]
    width = (bottom_right.x - top_left.x)
    height = (bottom_right.y - top_left.y)
    middle_x = (top_left.x + bottom_right.x) / 2
    middle_y = (top_left.y + bottom_right.y) / 2
    emoji = emoji.resize((width, height), resample=0).convert('RGBA')
    image.paste(emoji, (middle_x - width/2, middle_y - height/2), emoji)

# [START def_main]
def main(input_filename, output_filename):
    with open(input_filename, 'rb') as image:
        faces = detect_face(image)
        print('Found {} face{}'.format(
            len(faces), '' if len(faces) == 1 else 's'))
        if len(faces) > 0:
            print('Writing to file {}'.format(output_filename))
            # Reset the file pointer, so we can read the file again
            image.seek(0)
            highlight_faces(image, faces, output_filename)
# [END def_main]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Detects faces in the given image.')
    parser.add_argument(
        'input_image', help='the image you\'d like to detect faces in.')
    parser.add_argument(
        '--out', dest='output', default='out.jpg',
        help='the name of the output file.')
    args = parser.parse_args()

    main(args.input_image, args.output)
