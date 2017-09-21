"""Tensor-related utilities, AKA fun with ndarrays, NumPy, and SciPy.

https://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.html
https://docs.scipy.org/doc/numpy-1.13.0/index.html
https://docs.scipy.org/doc/scipy-0.19.1/reference/
"""
import os
from tempfile import TemporaryFile

import h5py
import numpy as np
from scipy import misc, ndimage

from pymoji.constants import OUTPUT_DIR, TEST_DATASET, TRAIN_DATASET, UPLOADS_DIR
from pymoji.emoji import extract_head, get_emoji_code
from pymoji.utils import get_json_name, json_to_object, load_json, process_folder


# enumeration of possible classifier outputs as ndarray
# subset of possible emoji codes in pymoji.emoji.HUMOR_RANK
# excludes codes based on the big guns for now
CLASSES = np.array([
    "1f622", # crying face
    "1f61e", # disappointed face
    "1f61f", # worried face
    "1f641", # slightly frowning face
    "1f620", # angry face
    "1f610", # neutral face
    "1f628", # fearful face
    "1f632", # astonished face
    "1f62e", # face with open mouth
    "1f62f", # hushed face
    "1f606", # smiling face with open mouth & closed eyes
    "1f601", # grinning face with smiling eyes
    "1f603", # smiling face with open mouth
    "1f60c", # relieved face
    "1f920", # cowboy hat face
    "1f642", # slightly smiling face
], ndmin=2) # shape (1, 16)

HEAD_SIZE = 64 # pixels
MINI_BATCH_SIZE = 100

# pylint: disable=invalid-name


def head_to_ndarray(input_stream, size=HEAD_SIZE):
    """Converts the given image into a tensor for use as input features. The
    input is normalized as a square RBG image of the given size, then flattened
    and returned as a 2D NumPy ndarray (not a vector).

    https://docs.scipy.org/doc/scipy/reference/ndimage.html
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.misc.imresize.html

    Examples:
    >>> from pymoji.constants import DEMO_PATH
    >>> head_to_ndarray(DEMO_PATH).shape
    (12288, 1)

    Args:
        input_stream: a BufferedIO image file-object
        size: integer pixel length of the sides of the square target image

    Returns:
        an ndarray of shape (size * size * 3, 1) containing the image data
    """
    pixel_ndarray = ndimage.imread(input_stream, flatten=False, mode='RGB')
    # just calls PIL under the hood
    pixel_ndarray = misc.imresize(pixel_ndarray, size=(size, size))
    tensor_length = size * size * 3 # RGB
    return pixel_ndarray.reshape((tensor_length, 1))


def load_all_heads(directory_path=UPLOADS_DIR):
    """Extracts example data from all images in the given input directory and
    returns the dataset as a pair of ndarrays X, Y.

    Args:
        directory_path: directory to go head-hunting in

    Returns:
        a pair of ndarrays X, Y
            X: features, shape (image size, number of examples)
            Y: labels, shape (number of classes, number of examples)
    """
    features = []
    labels = []

    def load_heads(input_path):
        """Helper for iteratively loading input feature data."""
        try:
            id_filename = os.path.basename(input_path)
            json_filename = get_json_name(id_filename)
            json_path = os.path.join(OUTPUT_DIR, json_filename)

            faces = None
            print('  loading: {}'.format(json_path))
            with open(json_path, 'r') as json_file:
                data = load_json(json_file)
                faces = json_to_object('annotations', data).faces

            print('  loading: {}'.format(input_path))
            with open(input_path, 'rb') as input_file:
                X, Y = extract_heads(input_file, faces)
                features.append(X)
                labels.append(Y)

        except Exception as error: # pylint: disable=broad-except
            print('  ERROR: {}'.format(error))

    process_folder(directory_path, load_heads)

    X = np.concatenate(features, axis=1)
    Y = np.concatenate(labels, axis=1)

    return X, Y


def extract_heads(image, faces):
    """Extracts example data from all heads in the given image using the given
    Google Vision API metadata. Returns the result as a ndarray
    with shape (flat image size, number of examples).

    Args:
        image: image file-object
        faces: Google Vision API metadata

    Returns:
        a pair of ndarrays X, Y
            X: features, shape (image size, number of examples)
            Y: labels, shape (number of classes, number of examples)
    """
    features = []
    labels = []

    for face in faces:
        # compute label Y
        code = get_emoji_code(None, face, use_gva_labels=False)
        # https://docs.scipy.org/doc/numpy-1.13.0/reference/generated/numpy.where.html
        y = np.where(CLASSES == code, 1, 0).T
        # compute features X
        head_image = extract_head(image, face, code)
        x = None
        with TemporaryFile() as head_stream:
            head_image.save(head_stream, format='JPEG')
            head_stream.seek(0)
            x = head_to_ndarray(head_stream)

        # add example
        features.append(x)
        labels.append(y)

    X = np.concatenate(features, axis=1)
    Y = np.concatenate(labels, axis=1)

    return X, Y


def save_dataset(X, Y, output_path=TRAIN_DATASET):
    """saves data"""
    with h5py.File(output_path, "w") as data_file:
        # todo deduplicate https://docs.scipy.org/doc/numpy/reference/generated/numpy.unique.html
        data_file.create_dataset("x", data=X)
        data_file.create_dataset("y", data=Y)


def load_dataset(train_path=TRAIN_DATASET, test_path=TEST_DATASET):
    """loads data"""
    train_dataset = h5py.File(train_path, "r")
    train_set_x_orig = np.array(train_dataset["x"][:])
    train_set_y_orig = np.array(train_dataset["y"][:])

    test_dataset = h5py.File(test_path, "r")
    test_set_x_orig = np.array(test_dataset["x"][:])
    test_set_y_orig = np.array(test_dataset["y"][:])

    train_set_y_orig = train_set_y_orig.reshape((1, train_set_y_orig.shape[0]))
    test_set_y_orig = test_set_y_orig.reshape((1, test_set_y_orig.shape[0]))

    return train_set_x_orig, train_set_y_orig, test_set_x_orig, test_set_y_orig


def random_mini_batches(X, Y, mini_batch_size=MINI_BATCH_SIZE):
    """Creates a list of random minibatches from the given features and labels.

    Args:
        X: input data, shape (input size, number of examples)
        Y: labels tensor, shape (number of classes, number of examples)
        mini_batch_size: integer size of the mini-batchess

    Returns:
        list of mini batches [(mini_batch_X, mini_batch_Y)]
    """
    # m = number of training examples
    m = X.shape[1]
    mini_batches = []
    #np.random.seed(seed) # for deterministic testing

    # shuffle (X, Y)
    permutation = list(np.random.permutation(m))
    shuffled_X = X[:, permutation]
    shuffled_Y = Y[:, permutation].reshape((Y.shape[0], m))

    # partition (shuffled_X, shuffled_Y) into complete mini batches
    for start in range(0, m, mini_batch_size):
        end = start + mini_batch_size
        mini_batch_X = shuffled_X[:, start:end]
        mini_batch_Y = shuffled_Y[:, start:end]
        mini_batch = (mini_batch_X, mini_batch_Y)
        mini_batches.append(mini_batch)

    # handling final partial mini batch (last mini-batch < mini_batch_size)
    remainder = m % mini_batch_size
    if remainder:
        mini_batch_X = shuffled_X[:, -remainder:]
        mini_batch_Y = shuffled_Y[:, -remainder:]
        mini_batch = (mini_batch_X, mini_batch_Y)
        mini_batches.append(mini_batch)

    return mini_batches


def one_hot(Y, C):
    """Converts the given labels tensor Y into one-hot encoding using the given
    classes tensor. The returned tensor has the same shape as Y.

    Args:
        Y: labels tensor, shape (number of classes, number of examples)
        C: classes tensor, shape (1, number of classes)

    Returns:
        one-hot encoded tensor, shape (number of classes, number of examples)
    """
    Y = np.eye(C)[Y.reshape(-1)].T
    return Y
