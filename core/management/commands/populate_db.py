from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import authenticate
from django.contrib.auth.models import User


from core.constants import (
    BLACKLISTED_ITEMS_APP_CONFIG_KEY,
    DEFAULT_IMAGGA_NSFW_CATORIZER_ID,
    IMAGGA_NSFW_CATORIZER_ID_APP_CONFIG_KEY,
    IMAGGA_NSFW_CHECK_FF_NAME,
    SAFETY_CONFIDENCE_THRESHOLD_APP_CONFIG_KEY,
)
from core.models import AppConfig, FeatureFlag


class Command(BaseCommand):
    def handle(self, *args, **options):
        current_user = self._create_base_superuser()

        if not current_user:
            raise CommandError("Invalid username or password!")

        if not current_user.is_superuser:
            raise CommandError("User must be a superuser!")

        # Create base AppConfig settings
        AppConfig.objects.create(
            key=IMAGGA_NSFW_CATORIZER_ID_APP_CONFIG_KEY,
            value=DEFAULT_IMAGGA_NSFW_CATORIZER_ID,
            created_by=current_user,
            modified_by=current_user,
        )
        AppConfig.objects.create(
            key=BLACKLISTED_ITEMS_APP_CONFIG_KEY,
            value="",
            created_by=current_user,
            modified_by=current_user,
        )
        AppConfig.objects.create(
            key=SAFETY_CONFIDENCE_THRESHOLD_APP_CONFIG_KEY,
            value=settings.IMAGE_SAFETY_CONFIDENCE_DEFAULT_THRESHOLD,
            created_by=current_user,
            modified_by=current_user,
        )

        # Create feature flags
        FeatureFlag.objects.create(
            name=IMAGGA_NSFW_CHECK_FF_NAME,
            active=False,
            created_by=current_user,
            modified_by=current_user,
        )

    def _create_base_superuser(self):
        print("Follow the prompts to create your superuser.")
        username = input("Please enter a username:")
        email = input("Please enter an email:")
        password = input("Please enter a password:")

        user = User.objects.create_superuser(
            username=username, email=email, password=password
        )

        return user
