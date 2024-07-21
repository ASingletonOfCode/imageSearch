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

    def list(self, request, *args, **kwargs):
        """
        A view that accepts GET with a query parameter of "objects" detected in the image
        """
        objects = request.query_params.get("objects", None)
        if objects is not None:
            queryset = Image.objects.filter(
                reduce(lambda x, y: x | y, [Q(detected_objects__icontains=object) for object in objects.split(",")])
            )
            serializer = ImageSerializer(queryset, many=True)
            return Response(
                data=serializer.data,
            )
        else:
            return super().list(request, *args, **kwargs)
