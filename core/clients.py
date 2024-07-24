from django.conf import settings
import requests
from logging import Logger
from core.constants import (
    DEFAULT_IMAGGA_NSFW_CATORIZER_ID,
    IMAGGA_NSFW_CATORIZER_ID_APP_CONFIG_KEY,
)

from core.models import AppConfig

log = Logger(__name__)

IMAGA_API_URL = "https://api.imagga.com/v2/"
TAG_URL = IMAGA_API_URL + "tags"
UPLOAD_URL = IMAGA_API_URL + "uploads"
CATEGORIES_CHECK_URL = IMAGA_API_URL + "categories"


class ImaggaClient:

    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

    def get_tag_image(self, image_url):
        response = requests.get(
            f"{TAG_URL}?image_url={image_url}", auth=(self.api_key, self.api_secret)
        )

        if response.status_code == 200:
            return response.json()
        else:
            self._error_response_handler(response)

    def get_tag_image_for_upload(self, upload_id):
        response = requests.get(
            f"{TAG_URL}?image_upload_id={upload_id}",
            auth=(self.api_key, self.api_secret),
        )

        if response.status_code == 200:
            return response.json()
        else:
            self._error_response_handler(response)

    def upload_image(self, image_path):
        response = requests.post(
            UPLOAD_URL,
            auth=(self.api_key, self.api_secret),
            files={"image": open(f"{settings.MEDIA_ROOT}/{image_path}", "rb")},
        )

        if response.status_code == 200:
            return response.json()
        else:
            self._error_response_handler(response)

    def check_nsfw_categories(self, image):
        try:
            imagga_nsfw_catorizer_id = AppConfig.objects.filter(
                key=IMAGGA_NSFW_CATORIZER_ID_APP_CONFIG_KEY
            ).get()
        except AppConfig.DoesNotExist:
            log.warn(
                f"Key of `{IMAGGA_NSFW_CATORIZER_ID_APP_CONFIG_KEY}` in AppConfig not found. Defaulting to hard-coded value."
            )
            imagga_nsfw_catorizer_id = DEFAULT_IMAGGA_NSFW_CATORIZER_ID

        response = requests.get(
            f"{CATEGORIES_CHECK_URL}/{imagga_nsfw_catorizer_id}?{f"image_url={image.source_url}" if image.source_url else f"image_upload_id={image.image_upload.upload_id}"}",
            auth=(self.api_key, self.api_secret),
        )

        if response.status_code == 200:
            return response.json()
        else:
            self._error_response_handler(response)

    def _error_response_handler(self, response):
        if response.status_code == 401:
            msg = "Unauthorized. Please check your API key and secret for Imagga."
        elif response.status_code == 404:
            msg = "Resource not found. Please check the URL."
        elif response.status_code == 400:
            msg = "Bad Request. Please check the request parameters."
        else:
            msg = f"An unexpected error occurred. Please try again later. Message: {response.message}"
        raise ValueError(msg)
