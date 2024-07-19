from django.shortcuts import render

from rest_framework import permissions, viewsets

from core.models import Image
from core.serializers import ImageSerializer


class ImageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows images to be fetched and uploaded
    """

    queryset = Image.objects.all().order_by("id")
    serializer_class = ImageSerializer
    permission_classes = [permissions.IsAuthenticated]
