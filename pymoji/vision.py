"""Wraps the Google Cloud Vision API to annotate images.

    https://googlecloudplatform.github.io/google-cloud-python/latest/vision/index.html#annotate-an-image
    https://googlecloudplatform.github.io/google-cloud-python/latest/vision/gapic/v1/types.html#google.cloud.vision_v1.types.Image
    https://googlecloudplatform.github.io/google-cloud-python/latest/vision/gapic/v1/types.html#google.cloud.vision_v1.types.ImageSource
    https://googlecloudplatform.github.io/google-cloud-python/latest/vision/gapic/v1/types.html#google.cloud.vision_v1.types.AnnotateImageRequest
    https://googlecloudplatform.github.io/google-cloud-python/latest/vision/gapic/v1/types.html#google.cloud.vision_v1.types.Feature
    https://googlecloudplatform.github.io/google-cloud-python/latest/vision/gapic/v1/types.html#google.cloud.vision_v1.types.AnnotateImageResponse
"""
from google.cloud.vision import enums, ImageAnnotatorClient, types

from pymoji import MAX_RESULTS


def to_vision_image(input_stream=None, input_uri=None):
    """Helper that converts various formats of given input image into a Google
    Cloud Vision API Image object. Pass the input image as either a BufferedIO
    stream (takes precedence), a Google Cloud Storage URI, or a publicly
    accessible URL.

    Args:
        input_stream: a BufferedIO stream containing an image with faces.
        input_uri: an image uri for either Google Cloud storage
            e.g. 'gs://bucket_name/path/to/image.jpg'
            or public HTTP/HTTP url
            e.g. 'http://cdn/path/to/image.jpg'

    Returns:
        a Google Cloud Vision API Image object
    """
    content = None
    source = None
    if input_stream:
        content = input_stream.read()
    elif input_uri:
        source = types.ImageSource(image_uri=input_uri) # pylint: disable=no-member
    return types.Image(content=content, source=source) # pylint: disable=no-member


def detect_faces(image):
    """Finds faces in the given input image and returns a list of Google Vision
    API Face Annotations.
    Currently uses MAX_RESULTS to limit how many labels come back.

    Args:
        image: a Google Cloud Vision API Image object with faces.

    Returns:
        a list of Face annotation objects found in the input image.
    """
    print('Detecting faces...')

    # This call to Google Vision API (ImageAnnotatorClient) will not work on local
    # if you don't have default application credentials. See README.
    # https://cloud.google.com/sdk/gcloud/reference/auth/application-default/login
    client = ImageAnnotatorClient()
    features = [{
        'type': enums.Feature.Type.FACE_DETECTION,
        'max_results': MAX_RESULTS
    }]
    faces = client.annotate_image({
        'image': image,
        'features': features
        }).face_annotations # pylint: disable=no-member

    print('...{} faces found.'.format(len(faces)))
    return faces


def detect_labels(image):
    """Finds labels in the given input image and returns a list of Google Vision
    API Label Annotations.
    Currently uses MAX_RESULTS to limit how many labels come back.

    Args:
        image: a Google Cloud Vision API Image object with faces.

    Returns:
        an array of Label annotation objects found in the input image.
    """
    print('Detecting labels...')

    client = ImageAnnotatorClient()
    features = [{
        'type': enums.Feature.Type.LABEL_DETECTION,
        'max_results': MAX_RESULTS
    }]
    labels = client.annotate_image({
        'image': image,
        'features': features
        }).label_annotations # pylint: disable=no-member

    print('...{} labels found.'.format(len(labels)))
    return labels
