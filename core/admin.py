from django.contrib import admin

from core.models import Image, ImageUpload

# Register your models here.

admin.site.register(Image)
admin.site.register(ImageUpload)
