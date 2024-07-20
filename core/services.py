from django.conf import settings
from core.clients import ImaggaClient
from core.models import Image, SourceType, ImageUpload


imagga_client = ImaggaClient(settings.IMAGGA_API_KEY, settings.IMAGGA_API_SECRET)


def process_image_upload(image: Image):
    """
    Process image upload by first determining the source type of the image and then using the appropriate client method to tag the image. Then stores
    the relevant models in the database.
    """
    if image.source_type == SourceType.UPLOAD:
        image.image_upload = upload_image(image)
        image.save()
        # TODO Check image categorization for blacklisted tags/objects before proceeding
        image_tag_response = imagga_client.get_tag_image_for_upload(
            image.image_upload.upload_id
        )
    elif image.source_type == SourceType.URL:
        image_tag_response = imagga_client.get_tag_image(image.source_url)
        # TODO Check image categorization for blacklisted tags/objects before proceeding
    else:
        raise ValueError("Invalid source type")
    image.detected_objects = _process_image_tags(image_tag_response)

    image.save()
    return image


def upload_image(image: Image):
    """
    Upload the image to Imagga and store the ImageUpload model in the database.
    """
    upload_response = imagga_client.upload_image(image.source)
    upload_id = upload_response["result"]["upload_id"]
    image_upload = ImageUpload.objects.create(
        image=image, upload_id=upload_id, status=upload_response["status"]["type"]
    )
    return image_upload


def _process_image_tags(image_response: dict):
    """
    Process the image tags from the Imagga API response and return a list of tags.
    """
    tags = image_response["result"]["tags"] or []

    temp = [tag["tag"]["en"] for tag in tags]
    print(temp)
    return temp
