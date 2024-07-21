from rest_framework import serializers
from core.models import Image
from core.services import process_image_upload


class ImageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Image
        fields = ["id", "label", "source_type", "source", "source_url", "detected_objects"]

    # TODO: Allow uppercase and lowercase source_type
    def create(self, validated_data):
        image = Image.objects.create(**{"uploaded_by":self.context["request"].user},  **validated_data)

        process_image_upload(image)
        
        return image
