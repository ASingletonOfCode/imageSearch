from rest_framework import viewsets

from django.contrib.auth.models import User


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("-date_joined")
    from imageSearch.serializers import UserSerializer  # Avoid circular import

    serializer_class = UserSerializer
