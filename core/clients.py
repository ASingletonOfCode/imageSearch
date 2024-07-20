from django.conf import settings
import requests

IMAGA_API_URL = "https://api.imagga.com/v2/"
TAG_URL = IMAGA_API_URL + "tags"
UPLOAD_URL = IMAGA_API_URL + "uploads"


class ImaggaClient:

    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

    def get_tag_image(self, image_url):
        response = requests.get(
            f"{TAG_URL}?image_url={image_url}", auth=(self.api_key, self.api_secret)
        )

        if response.status_code == 200:
            print(response.json())
            return response.json()
        else:
            # TODO handle error
            pass

    def get_tag_image_for_upload(self, upload_id):
        response = requests.get(
            f"{TAG_URL}?image_upload_id={upload_id}",
            auth=(self.api_key, self.api_secret),
        )

        if response.status_code == 200:
            print(response.json())
            return response.json()
        else:
            # TODO handle error
            pass

    def upload_image(self, image_path):
        response = requests.post(
            UPLOAD_URL,
            auth=(self.api_key, self.api_secret),
            files={"image": open(f"{settings.MEDIA_ROOT}/{image_path}", "rb")},
        )

        if response.status_code == 200:
            print(response.json())
            return response.json()
        else:
            # TODO handle error
            pass
