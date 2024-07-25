# Generated by Django 5.0.7 on 2024-07-19 15:36

import core.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ImageUpload",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("upload_id", models.CharField(max_length=100)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("SUCCESS", "success"),
                            ("ERROR", "error"),
                            ("PENDING", "pending"),
                            ("REJECTED", "rejected"),
                        ],
                        default=core.models.UploadStatusType["PENDING"],
                        max_length=15,
                    ),
                ),
                ("error_message", models.TextField(blank=True, null=True)),
                ("date_created", models.DateTimeField(auto_now_add=True)),
                ("date_updated", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Image",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("label", models.CharField(max_length=100, null=True, blank=True)),
                (
                    "source_type",
                    models.CharField(
                        choices=[("UPLOAD", "upload"), ("URL", "url")], max_length=15
                    ),
                ),
                (
                    "source",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to="%Y/%m/%d",
                        validators=[
                            django.core.validators.FileExtensionValidator(
                                ["jpg", "jpeg", "png"]
                            )
                        ],
                    ),
                ),
                ("date_created", models.DateTimeField(auto_now_add=True)),
                ("detected_objects", models.JSONField(blank=True, null=True)),
                ("blacklisted", models.BooleanField(default=False)),
                (
                    "uploaded_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "image_upload",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="core.imageupload",
                    ),
                ),
                ("source_url", models.URLField(blank=True, null=True)),
            ],
        ),
    ]
