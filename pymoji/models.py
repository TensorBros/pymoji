"""Schema metadata for JSON serialization.

Lightweight wrappers of Google Vision API models found here:
  https://cloud.google.com/vision/docs/reference/rest/v1/images/annotate
  https://googlecloudplatform.github.io/google-cloud-python/latest/vision/gapic/v1/api.html

Marshmallow JSON library documentation:
  http://marshmallow.readthedocs.io/en/latest/api_reference.html
  http://marshmallow.readthedocs.io/en/latest/quickstart.html
  http://marshmallow.readthedocs.io/en/latest/nesting.html
"""
from marshmallow import Schema, fields


# pylint: disable=missing-docstring,too-few-public-methods


class VertexSchema(Schema):
    class Meta:
        fields = ("x", "y")


class BoundingPolySchema(Schema):
    vertices = fields.Nested(VertexSchema, many=True)


class FaceSchema(Schema):
    bounding_poly = fields.Nested(BoundingPolySchema)

    class Meta:
        additional = (
                "detection_confidence",
                "sorrow_likelihood",
                "anger_likelihood",
                "surprise_likelihood",
                "headwear_likelihood",
                "joy_likelihood"
            )


class AnnotationsSchema(Schema):
    faces = fields.Nested(FaceSchema, many=True)
