from django.test import TestCase
import mock
import pytest

from core.clients import ImaggaClient
from core.models import Image, SourceType
from core.services import process_image_upload


@pytest.mark.django_db
class TestProcessImageUpload(TestCase):
    def setUp(self):
        pass

    @mock.patch.object(ImaggaClient, "upload_image")
    @mock.patch.object(ImaggaClient, "get_tag_image_for_upload")
    def test_process_image_upload_when_image_source_type_is_upload(
        self, mock_get_tag_image_for_upload, mock_upload_image
    ):
        # Arrange
        mock_upload_image.return_value = {
            "result": {"upload_id": "12345"},
            "status": {"text": "", "type": "success"},
        }
        mock_get_tag_image_for_upload.return_value = {
            "result": {
                "tags": [
                    {"confidence": 25.1324, "tag": {"en": "dog"}},
                    {"confidence": 15.1324, "tag": {"en": "cat"}},
                ]
            }
        }

        image = Image(source_type=SourceType.UPLOAD)

        # Act
        image = process_image_upload(image)

        # assert
        self.assertEqual(image.detected_objects, ["dog", "cat"])
        self.assertEqual(image.image_upload.upload_id, "12345")

    @mock.patch.object(ImaggaClient, "upload_image")
    @mock.patch.object(ImaggaClient, "get_tag_image")
    def test_process_image_upload_when_image_source_type_is_url(
        self, mock_get_tag_image, mock_upload_image
    ):
        # Arrange
        mock_get_tag_image.return_value = {
            "result": {
                "tags": [
                    {"confidence": 25.1324, "tag": {"en": "dog"}},
                    {"confidence": 15.1324, "tag": {"en": "cat"}},
                ]
            }
        }

        image = Image(
            source_type=SourceType.URL, source_url="https://example.com/image.jpg"
        )

        # Act
        image = process_image_upload(image)

        # assert
        mock_upload_image.assert_not_called()
        self.assertEqual(image.detected_objects, ["dog", "cat"])
        # image_upload should only be created when the system has to upload the image to Imagga first
        self.assertIsNone(image.image_upload)
