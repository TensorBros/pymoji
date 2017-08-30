"""Wraps the Google Cloud Vision API to annotate images."""
from google.cloud.vision import enums, ImageAnnotatorClient, types

from pymoji import MAX_RESULTS


def detect_faces(input_stream=None, input_uri=None):
    """Uses the Vision API to detect faces in an input image. Pass the input
    image as either a BufferedIO stream (takes precedence) or a Google Cloud
    Storage URI.

    https://googlecloudplatform.github.io/google-cloud-python/latest/vision/index.html#annotate-an-image
    https://googlecloudplatform.github.io/google-cloud-python/latest/vision/gapic/v1/types.html#google.cloud.vision_v1.types.Image
    https://googlecloudplatform.github.io/google-cloud-python/latest/vision/gapic/v1/types.html#google.cloud.vision_v1.types.ImageSource
    https://googlecloudplatform.github.io/google-cloud-python/latest/vision/gapic/v1/types.html#google.cloud.vision_v1.types.AnnotateImageRequest
    https://googlecloudplatform.github.io/google-cloud-python/latest/vision/gapic/v1/types.html#google.cloud.vision_v1.types.Feature
    https://googlecloudplatform.github.io/google-cloud-python/latest/vision/gapic/v1/types.html#google.cloud.vision_v1.types.AnnotateImageResponse

    Args:
        input_stream: a BufferedIO stream containing an image with faces.
        input_uri: an image uri for either Google Cloud storage
            e.g. 'gs://bucket_name/path/to/image.jpg'
            or public HTTP/HTTP url
            e.g. 'http://cdn/path/to/image.jpg'

    Returns:
        an array of Face annotation objects found in the input image.
    """
    print('Detecting faces...')
    client = ImageAnnotatorClient()

    # convert input image to Google Cloud Image
    content = None
    source = None
    if input_stream:
        content = input_stream.read()
    elif input_uri:
        source = types.ImageSource(image_uri=input_uri) # pylint: disable=no-member
    image = types.Image(content=content, source=source) # pylint: disable=no-member

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


def detect_labels(input_stream=None, input_uri=None):
    """Uses the Vision API to detect labels in an input image. Pass the input
    image as either a BufferedIO stream (takes precedence) or a Google Cloud
    Storage URI.

    https://googlecloudplatform.github.io/google-cloud-python/latest/vision/index.html#annotate-an-image
    https://googlecloudplatform.github.io/google-cloud-python/latest/vision/gapic/v1/types.html#google.cloud.vision_v1.types.Image
    https://googlecloudplatform.github.io/google-cloud-python/latest/vision/gapic/v1/types.html#google.cloud.vision_v1.types.ImageSource
    https://googlecloudplatform.github.io/google-cloud-python/latest/vision/gapic/v1/types.html#google.cloud.vision_v1.types.AnnotateImageRequest
    https://googlecloudplatform.github.io/google-cloud-python/latest/vision/gapic/v1/types.html#google.cloud.vision_v1.types.Feature
    https://googlecloudplatform.github.io/google-cloud-python/latest/vision/gapic/v1/types.html#google.cloud.vision_v1.types.AnnotateImageResponse

    Args:
        input_stream: a BufferedIO stream containing an image.
        input_uri: an image uri for either Google Cloud storage
            e.g. 'gs://bucket_name/path/to/image.jpg'
            or public HTTP/HTTP url
            e.g. 'http://cdn/path/to/image.jpg'

    Returns:
        an array of Label annotation objects found in the input image.
    """
    print('Detecting labels...')
    client = ImageAnnotatorClient()

    # convert input image to Google Cloud Image
    content = None
    source = None
    if input_stream:
        content = input_stream.read()
    elif input_uri:
        source = types.ImageSource(image_uri=input_uri) # pylint: disable=no-member
    image = types.Image(content=content, source=source) # pylint: disable=no-member

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
