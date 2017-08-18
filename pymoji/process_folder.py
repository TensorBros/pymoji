from __future__ import absolute_import, print_function, unicode_literals
import os

import PIL

from pymoji import faces
from pymoji.app import OUTPUT_DIR


#TODO put this into a helper/utilities file if it's used by both process_folder and faces.py
def generate_output_path(input_image):
    # mkdir if OUTPUT_DIR doesn't exist?
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    filename = input_image.split('.')[-2]
    extension = input_image.split('.')[-1]
    output_image = filename + "-output." + extension
    return os.path.join(OUTPUT_DIR, output_image)


def process_folder(path):
    for file_name in os.listdir(path):
        actual_file_location = os.path.join(path, file_name)
        is_jpg = (os.path.splitext(file_name)[1] == '.jpg' or os.path.splitext(file_name)[1] == '.JPG')

        if os.path.isfile(actual_file_location) and is_jpg:
            image = PIL.Image.open(actual_file_location)
            try:
                image.load()
                print('processing ' + os.path.splitext(file_name)[0])
                output_path = generate_output_path(file_name)
                faces.main(os.path.join(path, file_name), output_path)
            except IOError as e:
                print('Bad image: %s' % e)
        else:
            print('skipped non-image file')
