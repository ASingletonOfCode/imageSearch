from rest_framework import serializers
from core.models import Image
from core.services import process_image_upload


class ImageSerializer(serializers.HyperlinkedModelSerializer):
    detect_objects = serializers.BooleanField(read_only=True, default=True)

    class Meta:
        model = Image
        fields = [
            "id",
            "label",
            "source_type",
            "source",
            "source_url",
            "detected_objects",
            "detect_objects",
        ]

    # TODO: Allow uppercase and lowercase source_type
    def create(self, validated_data):
        image = Image.objects.create(
            **{"uploaded_by": self.context["request"].user}, **validated_data
        )

        if bool(self.data.get("detect_objects")) == True:
            process_image_upload(image)
        else:
            # TODO: Log that image was not processed
            pass

        return image
