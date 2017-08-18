# Copyright 2016, Google, Inc.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from PIL import Image

from pymoji.faces import main
from pymoji.app import RESOURCES, OUTPUT_DIR


def test_main(tmpdir):
    out_file = os.path.join(OUTPUT_DIR, 'face-output.jpg')
    in_file = os.path.join(RESOURCES, 'face-input.jpg')

    # Make sure there isn't already a green box
    im = Image.open(in_file)
    pixels = im.getdata()
    unnatural_face_yellow = sum(1 for (r, g, b) in pixels if r == 251 and g == 200 and b == 83)
    assert unnatural_face_yellow < 1

    main(in_file, out_file)

    # Make sure there now is some green drawn
    im = Image.open(out_file)
    pixels = im.getdata()
    unnatural_face_yellow = sum(1 for (r, g, b) in pixels if r == 251 and g == 200 and b == 83)
    assert unnatural_face_yellow > 10
