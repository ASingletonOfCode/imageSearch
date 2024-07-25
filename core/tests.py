import io
from logging import Logger
from rest_framework.exceptions import ValidationError, ErrorDetail
from django.test import TestCase
import mock
import pytest

from core.clients import ImaggaClient
from core.models import AppConfig, FeatureFlag, Image, SourceType
from core.constants import IMAGGA_NSFW_CHECK_FF_NAME
from core.services import (
    get_blacklisted_items,
    process_image_upload,
    validate_blacklisted_items,
    validate_nsfw,
)

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from core.serializers import ImageSerializer
from django.contrib.auth.models import User


@mock.patch("core.views.process_image_upload")
@mock.patch.object(Logger, "info")
@mock.patch.object(Logger, "warn")
class ImageViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")
        self.image_data = {
            "label": "Test Image",
            "source_type": "UPLOAD",
            "source": self._generate_photo_file(),
            "detect_objects": True,
        }

    def test_create_image_success(
        self, mock_warn, mock_info, mock_process_image_upload
    ):
        # Arrange
        url = reverse("image-list")

        # Act
        response = self.client.post(url, self.image_data, format="multipart")

        # Assert
        result_image = Image.objects.get(id=response.data["id"])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, result_image.to_dict())
        mock_process_image_upload.assert_called_with(result_image)
        mock_info.assert_not_called()
        mock_warn.assert_not_called()

    def test_skip_object_detection(
        self, mock_warn, mock_info, mock_process_image_upload
    ):
        # Arrange
        url = reverse("image-list")
        self.image_data["detect_objects"] = False

        # Act
        response = self.client.post(url, self.image_data, format="multipart")

        # Assert
        result_image = Image.objects.get(id=response.data["id"])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_process_image_upload.assert_not_called()
        mock_info.assert_called_with(
            f"Skipping object detection for image: {result_image.id}"
        )
        mock_warn.assert_not_called()

    def test_list_images_with_objects_returns_images_that_match_all_requested_objects(
        self, mock_warn, mock_info, mock_process_image_upload
    ):
        # Arrange
        Image.objects.create(
            label="Image 1", detected_objects="cat,dog", uploaded_by=self.user
        )
        Image.objects.create(
            label="Image 2", detected_objects="dog", uploaded_by=self.user
        )
        url = reverse("image-list")

        # Act
        response = self.client.get(url, {"objects": "dog,cat"})

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        mock_process_image_upload.assert_not_called()
        mock_info.assert_not_called()
        mock_warn.assert_not_called()

    def test_handle_validation_error(
        self, mock_warn, mock_info, mock_process_image_upload
    ):
        # Arrange
        url = reverse("image-list")
        self.image_data["source"] = ""

        # Act
        response = self.client.post(url, self.image_data, format="multipart")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)
        mock_process_image_upload.assert_not_called()
        mock_info.assert_not_called()
        mock_warn.assert_not_called()

    def _generate_photo_file(self):
        file = io.BytesIO()
        from PIL import Image as PILImage

        image = PILImage.new("RGBA", size=(100, 100), color=(155, 0, 0))
        image.save(file, "png")
        file.name = "test.png"
        file.seek(0)
        return file


@pytest.mark.django_db
class TestProcessImageUpload(TestCase):
    def setUp(self):
        FeatureFlag.objects.create(name=IMAGGA_NSFW_CHECK_FF_NAME, active=True)

    @mock.patch.object(ImaggaClient, "upload_image")
    @mock.patch.object(ImaggaClient, "get_tag_image_for_upload")
    @mock.patch("core.services.validate_nsfw", return_value=True)
    @mock.patch("core.services.validate_blacklisted_items", return_value=True)
    def test_process_image_upload_when_image_source_type_is_upload_and_passes_nsfw_checks(
        self,
        mock_blacklisted_items,
        mock_validate_nsfw,
        mock_get_tag_image_for_upload,
        mock_upload_image,
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

        image = Image(id=1, source_type=SourceType.UPLOAD.name)

        # Act
        process_image_upload(image)

        # assert
        self.assertEqual(image.detected_objects, ["dog", "cat"])
        self.assertEqual(image.image_upload.upload_id, "12345")

    @mock.patch.object(ImaggaClient, "upload_image")
    @mock.patch.object(ImaggaClient, "get_tag_image_for_upload")
    @mock.patch("core.services.validate_nsfw", return_value=False)
    @mock.patch("core.services.validate_blacklisted_items", return_value=True)
    @mock.patch.object(Logger, "warn")
    def test_process_image_upload_when_image_source_type_is_upload_but_fails_nsfw_check(
        self,
        mock_warn_logger,
        mock_blacklisted_items,
        mock_validate_nsfw,
        mock_get_tag_image_for_upload,
        mock_upload_image,
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

        image = Image(id=1, source_type=SourceType.UPLOAD.name)

        # Act
        with self.assertRaises(ValidationError) as ve:
            process_image_upload(image)

        # assert
        self.assertEqual(image.detected_objects, ["dog", "cat"])
        self.assertIsNotNone(image.image_upload)
        mock_warn_logger.assert_called_once_with(
            f"Image {image.id} contains NSFW content. Image blacklisted."
        )
        self.assertEqual(
            ve.exception.detail,
            [ErrorDetail(string="Image contains NSFW content.", code="invalid")],
        )

    @mock.patch.object(ImaggaClient, "upload_image")
    @mock.patch.object(ImaggaClient, "get_tag_image_for_upload")
    @mock.patch("core.services.validate_nsfw", return_value=True)
    @mock.patch("core.services.validate_blacklisted_items", return_value=False)
    @mock.patch.object(Logger, "warn")
    def test_process_image_upload_when_image_source_type_is_upload_but_fails_blacklisted_items_check(
        self,
        mock_warn_logger,
        mock_blacklisted_items,
        mock_validate_nsfw,
        mock_get_tag_image_for_upload,
        mock_upload_image,
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

        image = Image(id=1, source_type=SourceType.UPLOAD.name)

        # Act
        with self.assertRaises(ValidationError) as ve:
            process_image_upload(image)

        # assert
        self.assertEqual(image.detected_objects, ["dog", "cat"])
        self.assertIsNotNone(image.image_upload)
        mock_warn_logger.assert_called_once_with(
            f"Image {image.id} contains NSFW content. Image blacklisted."
        )
        self.assertEqual(
            ve.exception.detail,
            [ErrorDetail(string="Image contains NSFW content.", code="invalid")],
        )

    @mock.patch.object(ImaggaClient, "upload_image")
    @mock.patch.object(ImaggaClient, "get_tag_image")
    @mock.patch("core.services.validate_nsfw", return_value=True)
    @mock.patch("core.services.validate_blacklisted_items", return_value=True)
    def test_process_image_upload_when_image_source_type_is_url_and_passes_nsfw_checks(
        self,
        mock_blacklisted_items,
        mock_validate_nsfw,
        mock_get_tag_image,
        mock_upload_image,
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
            id=1,
            source_type=SourceType.URL.name,
            source_url="https://example.com/image.jpg",
        )

        # Act
        process_image_upload(image)

        # assert
        mock_upload_image.assert_not_called()
        self.assertEqual(image.detected_objects, ["dog", "cat"])
        # image_upload should only be created when the system has to upload the image to Imagga first
        self.assertIsNone(image.image_upload)

    @mock.patch.object(ImaggaClient, "upload_image")
    @mock.patch.object(ImaggaClient, "get_tag_image")
    @mock.patch("core.services.validate_nsfw", return_value=False)
    @mock.patch("core.services.validate_blacklisted_items", return_value=True)
    @mock.patch.object(Logger, "warn")
    def test_process_image_upload_when_image_source_type_is_url_but_fails_nsfw_check(
        self,
        mock_warn_logger,
        mock_blacklisted_items,
        mock_validate_nsfw,
        mock_get_tag_image,
        mock_upload_image,
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
            id=1,
            source_type=SourceType.URL.name,
            source_url="https://example.com/image.jpg",
        )

        # Act
        with self.assertRaises(ValidationError) as ve:
            process_image_upload(image)

        # assert
        mock_upload_image.assert_not_called()
        self.assertEqual(image.detected_objects, ["dog", "cat"])
        # image_upload should only be created when the system has to upload the image to Imagga first
        self.assertIsNone(image.image_upload)
        mock_warn_logger.assert_called_once_with(
            f"Image {image.id} contains NSFW content. Image blacklisted."
        )
        self.assertEqual(
            ve.exception.detail,
            [ErrorDetail(string="Image contains NSFW content.", code="invalid")],
        )

    @mock.patch.object(ImaggaClient, "upload_image")
    @mock.patch.object(ImaggaClient, "get_tag_image")
    @mock.patch("core.services.validate_nsfw", return_value=True)
    @mock.patch("core.services.validate_blacklisted_items", return_value=False)
    @mock.patch.object(Logger, "warn")
    def test_process_image_upload_when_image_source_type_is_url_but_fails_blacklisted_item_check(
        self,
        mock_warn_logger,
        mock_blacklisted_items,
        mock_validate_nsfw,
        mock_get_tag_image,
        mock_upload_image,
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
            id=1,
            source_type=SourceType.URL.name,
            source_url="https://example.com/image.jpg",
        )

        # Act
        with self.assertRaises(ValidationError) as ve:
            process_image_upload(image)

        # assert
        mock_upload_image.assert_not_called()
        self.assertEqual(image.detected_objects, ["dog", "cat"])
        # image_upload should only be created when the system has to upload the image to Imagga first
        self.assertIsNone(image.image_upload)
        mock_warn_logger.assert_called_once_with(
            f"Image {image.id} contains NSFW content. Image blacklisted."
        )
        self.assertEqual(
            ve.exception.detail,
            [ErrorDetail(string="Image contains NSFW content.", code="invalid")],
        )

    @mock.patch.object(Logger, "warn")
    @mock.patch.object(ImaggaClient, "check_nsfw_categories")
    def test_validate_nsfw_returns_false_if_image_contains_nsfw_content(
        self, mock_check_nsfw_categories, mock_warn_log
    ):
        # Arrange
        image = mock.Mock(Image)

        mock_check_nsfw_categories.return_value = {
            "result": {
                "categories": [
                    {"confidence": 50, "name": {"en": "safe"}},
                    {"confidence": 50, "name": {"en": "naughty_stuff"}},
                ]
            },
            "status": {"text": "en", "type": "success"},
        }

        # Act
        result = validate_nsfw(image)

        # Assert
        self.assertFalse(result)
        assert mock_warn_log.mock_calls == [
            mock.call(
                "Key of `safety_confidence_threshold` in AppConfig not found. Defaulting to hard-coded value."
            ),
            mock.call(f"Image {image.id} contains NSFW content. Image blacklisted."),
        ]
        self.assertTrue(image.blacklisted)

    @mock.patch("core.services.get_blacklisted_items", return_value=["dog"])
    def test_images_detected_objects_does_contains_blacklisted_items(
        self, mock_blacklisted_items
    ):
        # Arrange
        image = mock.Mock(Image)
        image.detected_objects = ["dog", "cat"]

        # Act
        result = validate_blacklisted_items(image)

        # Assert
        self.assertFalse(result)
        self.assertTrue(image.blacklisted)

    @mock.patch("core.services.get_blacklisted_items", return_value=["cow"])
    def test_images_detected_objects_does_not_contain_blacklisted_items(
        self, mock_blacklisted_items
    ):
        # Arrange
        image = mock.Mock(Image)
        image.detected_objects = ["dog", "cat"]
        image.blacklisted = None

        # Act
        result = validate_blacklisted_items(image)

        # Assert
        self.assertTrue(result)
        self.assertIsNone(image.blacklisted)

    def test_get_blacklisted_items(self):
        # Arrange
        AppConfig.objects.create(key="blacklisted_items", value="dog,cat")

        # Act
        result = get_blacklisted_items()
        self.assertEqual(result, ["dog", "cat"])
