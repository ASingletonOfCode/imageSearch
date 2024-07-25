from functools import reduce
from django.db.models import Q

from rest_framework import permissions, viewsets
from rest_framework.response import Response

from core.models import Image
from core.serializers import ImageSerializer
from logging import Logger
from rest_framework import status
from rest_framework.exceptions import ValidationError

from core.services import process_image_upload

log = Logger(__name__)


class ImageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows images to be fetched and uploaded
    """

    queryset = Image.objects.all().order_by("id")
    serializer_class = ImageSerializer
    permission_classes = [permissions.IsAuthenticated]

    # TODO: Allow uppercase and lowercase source_type
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        detect_objects = data.get("detect_objects", "false").lower() == "true"
        del data["detect_objects"]

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        try:
            image = Image.objects.create(
                **{"uploaded_by": self.request.user}, **serializer.validated_data
            )
            if detect_objects:
                process_image_upload(image)
            else:
                log.info(f"Skipping object detection for image: {image.id}")

            headers = self.get_success_headers(serializer.data)
            return Response(image.to_dict(), status=status.HTTP_200_OK, headers=headers)
        except ValidationError as e:
            log.warn(f"Exception while processing image: {e.detail}")
            raise

    def list(self, request, *args, **kwargs):
        """
        A view that accepts GET with a query parameter of "objects" detected in the image
        """
        objects = request.query_params.get("objects", None)
        blacklisted = request.query_params.get("blacklisted", False)

        if objects is not None:
            queryset = Image.objects.filter(blacklisted=blacklisted).filter(
                reduce(
                    lambda x, y: x & y,
                    [
                        Q(detected_objects__icontains=object)
                        for object in objects.split(",")
                    ],
                )
            )
            serializer = ImageSerializer(queryset, many=True)
            return Response(
                data=serializer.data,
            )
        else:
            return super().list(request, *args, **kwargs)

    def handle_exception(self, exc):
        if isinstance(exc, ValidationError):
            return Response({"detail": exc.detail}, status=exc.status_code)
        return super().handle_exception(exc)
