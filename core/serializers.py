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

    def validate(self, data):
        if data["source_type"] == "UPLOAD" and not data.get("source"):
            raise serializers.ValidationError(
                "source is required for source_type=upload"
            )
        if data["source_type"] == "URL" and not data.get("source_url"):
            raise serializers.ValidationError(
                "source_url is required for source_type=url"
            )
        return data
