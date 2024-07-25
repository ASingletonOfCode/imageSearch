from django.conf import settings
from rest_framework.exceptions import ValidationError
from core.clients import ImaggaClient
from core.constants import (
    BLACKLISTED_ITEMS_APP_CONFIG_KEY,
    IMAGGA_NSFW_CHECK_FF_NAME,
    SAFETY_CONFIDENCE_THRESHOLD_APP_CONFIG_KEY,
)
from core.models import AppConfig, FeatureFlag, Image, SourceType, ImageUpload
from logging import Logger

log = Logger(__name__)

imagga_client = ImaggaClient(settings.IMAGGA_API_KEY, settings.IMAGGA_API_SECRET)


def process_image_upload(image: Image):
    """
    Process image upload by first determining the source type of the image and then using the appropriate client method to tag the image. Then stores
    the relevant models in the database.

    :param image: Image object
    """
    try:
        nsfw_check_ff = FeatureFlag.objects.get(name=IMAGGA_NSFW_CHECK_FF_NAME)
    except FeatureFlag.DoesNotExist:
        log.warn(
            f"Feature flag {IMAGGA_NSFW_CHECK_FF_NAME} not found. Skipping NSFW check."
        )
        nsfw_check_ff = None

    if image.source_type == SourceType.UPLOAD.name:
        image.image_upload = upload_image(image)
        image_tag_response = imagga_client.get_tag_image_for_upload(
            image.image_upload.upload_id
        )
        image.detected_objects = _process_image_tags(image_tag_response)
        if (
            nsfw_check_ff and nsfw_check_ff.active and not validate_nsfw(image)
        ) or not validate_blacklisted_items(image):
            log.warn(f"Image {image.id} contains NSFW content. Image blacklisted.")
            # TODO ensure image artifact is not stored in our system
            raise ValidationError("Image contains NSFW content.")
    elif image.source_type == SourceType.URL.name:
        image_tag_response = imagga_client.get_tag_image(image.source_url)
        image.detected_objects = _process_image_tags(image_tag_response)
        if (
            nsfw_check_ff and nsfw_check_ff.active and not validate_nsfw(image)
        ) or not validate_blacklisted_items(image):
            log.warn(f"Image {image.id} contains NSFW content. Image blacklisted.")
            # TODO ensure image artifact is not stored in our system
            raise ValidationError("Image contains NSFW content.")

    else:
        raise ValueError("Invalid source type")

    image.save()


def upload_image(image: Image):
    """
    Upload the image to Imagga and store the ImageUpload model in the database.

    :param image: Image object
    :return: ImageUpload object
    """
    try:
        upload_response = imagga_client.upload_image(image.source)
    except Exception as e:
        raise ValueError(f"Exception while uploading image: {e}")
    upload_id = upload_response["result"]["upload_id"]
    image_upload = ImageUpload.objects.create(
        image=image, upload_id=upload_id, status=upload_response["status"]["type"]
    )
    return image_upload


def validate_nsfw(image: Image):
    """
    Validate if the image contains NSFW content using the Imagga NSFW categorizer.

    :param image: Image object
    :return: False if image contains NSFW content, True otherwise
    """

    SAFETY_CONFIDENCE_THRESHOLD = settings.IMAGE_SAFETY_CONFIDENCE_DEFAULT_THRESHOLD
    try:
        SAFETY_CONFIDENCE_THRESHOLD = float(
            AppConfig.objects.filter(
                key=SAFETY_CONFIDENCE_THRESHOLD_APP_CONFIG_KEY
            ).get()
        )
    except AppConfig.DoesNotExist:
        log.warn(
            f"Key of `{SAFETY_CONFIDENCE_THRESHOLD_APP_CONFIG_KEY}` in AppConfig not found. Defaulting to hard-coded value."
        )

    categories_check_response = imagga_client.check_nsfw_categories(image)

    safety_confidence = 0
    if (
        "status" in categories_check_response
        and "text" in categories_check_response["status"]
        and categories_check_response["status"]["type"] == "success"
        and "result" in categories_check_response
        and "categories" in categories_check_response["result"]
    ):
        for category in categories_check_response["result"]["categories"]:
            if category.get("name") and category.get("name").get("en") == "safe":
                safety_confidence = category.get("confidence", 0)
                break

        if safety_confidence < SAFETY_CONFIDENCE_THRESHOLD:
            image.blacklisted = True
            image.save()
            log.warn(f"Image {image.id} contains NSFW content. Image blacklisted.")
            return False
    else:
        log.warn(
            f"Unable to determine NSFW content for image {image.id} based on response. Skipping NSFW check."
        )
    return True


def validate_blacklisted_items(image: Image):
    """
    Validate if the image contains blacklisted items.

    :param image: Image object
    :return: False if image contains blacklisted items, True otherwise
    """
    blacklisted_items = set(
        blacklisted_items if (blacklisted_items := get_blacklisted_items()) else []
    )

    detected_objects_blacklisted_items_intersection = set(
        image.detected_objects
    ).intersection(blacklisted_items)

    if detected_objects_blacklisted_items_intersection:
        image.blacklisted = True
        image.save()
        log.warn(f"Image {image.id} contains blacklisted items. Image blacklisted.")
        return False
    return True


def get_blacklisted_items():
    """
    Get blacklisted items from the AppConfig model.
    """
    try:
        blacklisted_items_app_config = AppConfig.objects.filter(
            key=BLACKLISTED_ITEMS_APP_CONFIG_KEY
        ).get()
    except AppConfig.DoesNotExist:
        log.warn(
            f"Key of `{BLACKLISTED_ITEMS_APP_CONFIG_KEY}` in AppConfig not found. Skipping blacklisted items check."
        )
    return blacklisted_items_app_config.value.split(",")


def _process_image_tags(image_response: dict, language_encoding="en"):
    """
    Process the image tags from the Imagga API response and return a list of tags.
    """
    return [
        tag["tag"][language_encoding] for tag in image_response["result"]["tags"] or []
    ]
