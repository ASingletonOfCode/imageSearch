from enum import Enum
from django.db import models

class SourceType(Enum):
    UPLOAD = 'upload'
    URL = 'url'

class UploadStatusType(Enum):
    SUCCESS = 'success'
    ERROR = 'error'

class Image(models.Model):
    label = models.CharField(max_length=100)
    source_type = models.CharField(choices=[(tag.name, tag.value) for tag in SourceType])
    source = models.ImageField(upload_to='images/', null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    detected_objects = models.JSONField(null=True, blank=True)
    uploaded_by = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, blank=True)
    upload_id = models.CharField(max_length=100, null=True, blank=True)
    upload_status_type = models.CharField(choices=[(tag.name, tag.value) for tag in UploadStatusType], null=True, blank=True)
    blacklisted = models.BooleanField(default=False)