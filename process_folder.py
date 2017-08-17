#!/usr/bin/env python

import argparse
import os
import faces
import PIL

def process_folder(path):
    for file_name in os.listdir(path):
        actual_file_location = os.path.join(path, file_name)
        is_jpg = (os.path.splitext(file_name)[1] == '.jpg' or os.path.splitext(file_name)[1] == '.JPG')

        if os.path.isfile(actual_file_location) and is_jpg:
            image = PIL.Image.open(actual_file_location)
            try:
                image.load()
                print('processing ' + os.path.splitext(file_name)[0])
                result_file = os.path.splitext(file_name)[0] + '_emojied.jpg'
                faces.main(os.path.join(path, file_name), os.path.join(path, result_file), 5)             
            except IOError as e:
                print 'Bad image: %s' % e
        else:
            print('skipped non-image file')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Process a directory of photos into emojifaces')
    parser.add_argument(
        'path', help='path to the target directory')
    args = parser.parse_args()

    process_folder(args.path)
