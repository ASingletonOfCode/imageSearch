from django.contrib import admin

from core.models import AppConfig, FeatureFlag, Image, ImageUpload

# Register your models here.

admin.site.register(Image)
admin.site.register(ImageUpload)
admin.site.register(AppConfig)
admin.site.register(FeatureFlag)
