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
    label = models.CharField(max_length=100, null=True, blank=True)
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
        return f"""Id: {self.id}
Image: {self.label}
{self.source and f"Source: {self.source}"}
{self.source_url and f"Source Url: {self.source_url}"}
"""

    def to_dict(self):
        return {
            "id": self.id,
            "label": self.label,
            "image_upload_id": self.image_upload.id if self.image_upload else None,
            "source_type": self.get_source_type_display(),  # Gets the human-readable name for the Enum choice
            "source_url": self.source_url,
            "source": (self.source.url if self.source else None),
            "date_created": self.date_created.isoformat(),  # Convert datetime to ISO format string
            "detected_objects": self.detected_objects,
            "uploaded_by_id": self.uploaded_by.id if self.uploaded_by else None,
            "uploaded_by_username": (
                self.uploaded_by.username if self.uploaded_by else None
            ),
            "blacklisted": self.blacklisted,
        }


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


class AppConfig(models.Model):
    """
    Class to store the AppConfig for the application
    """

    key = models.CharField(max_length=100, unique=True)
    value = models.TextField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="created_app_config",  # Unique related_name for created_by
    )
    modified_by = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="modified_app_config",  # Unique related_name for modified_by
    )

    def __str__(self):
        return f"Key: {self.key} -- Value: {self.value}  -- Created By: {self.created_by.username} -- Modified By: {self.modified_by.username}"


class FeatureFlag(models.Model):
    """
    Class to store the FeatureFlag for the application
    """

    name = models.CharField(max_length=100, unique=True)
    active = models.BooleanField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="created_feature_flags",  # Unique related_name for created_by
    )
    modified_by = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="modified_feature_flags",  # Unique related_name for modified_by
    )

    def __str__(self):
        return f"Name: {self.name} -- Is Active: {self.active} -- Created By: {self.created_by.username} -- Last Modified By: {self.modified_by.username}"
