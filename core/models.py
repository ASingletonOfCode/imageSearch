from enum import Enum
from django.db import models
from django.core.validators import FileExtensionValidator


class SourceType(Enum):
    UPLOAD = "upload"
    URL = "url"


class UploadStatusType(Enum):
    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"
    REJECTED = "rejected"  # Image is blacklisted and therefore not persisted


class Image(models.Model):
    label = models.CharField(max_length=100)
    image_upload = models.ForeignKey(
        "ImageUpload", on_delete=models.CASCADE, null=True, blank=True
    )
    source_type = models.CharField(
        choices=[(tag.name, tag.value) for tag in SourceType],
        max_length=15,
    )
    source_url = models.URLField(null=True, blank=True)
    source = models.ImageField(
        upload_to="%Y/%m/%d",
        null=True,
        blank=True,
        validators=[FileExtensionValidator(["jpg", "jpeg", "png"])],
    )
    date_created = models.DateTimeField(auto_now_add=True)
    detected_objects = models.JSONField(null=True, blank=True)
    uploaded_by = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE, null=True, blank=True
    )
    blacklisted = models.BooleanField(default=False)

    def __str__(self):
        return f"""Image: {self.label}
Source Type: {self.source_type}
Source URL: {self.source_url}
Source: {self.source}
Date Created: {self.date_created}
Detected Objects: {self.detected_objects}
Uploaded By: {self.uploaded_by}
Blacklisted: {self.blacklisted}
"""


class ImageUpload(models.Model):
    """
    Class to track the Image Upload, since Imagga has a 24 hr TTL for the uploaded image
    """

    upload_id = models.CharField(max_length=100)
    status = models.CharField(
        choices=[(tag.name, tag.value) for tag in UploadStatusType],
        default=UploadStatusType.PENDING,
        max_length=15,
    )
    error_message = models.TextField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
