from rest_framework import serializers
from core.models import Image


class ImageSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Image
        fields = [
            "id",
            "label",
            "source_type",
            "source",
            "source_url",
            "detected_objects",
        ]
