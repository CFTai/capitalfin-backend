from django.core.validators import FileExtensionValidator

from rest_framework import serializers

from . import models


class UploadSerializer(serializers.ModelSerializer):
    file_data = serializers.FileField(
        validators=[FileExtensionValidator(["png", "jpg", "jpeg", "webp"])],
        write_only=True,
    )
    name = serializers.CharField(source="file_data.name", read_only=True)
    url = serializers.CharField(source="file_data.url", read_only=True)

    class Meta:
        model = models.Upload
        fields = "__all__"

    def validate_file_data(self, value):
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("File size cannot exceed 5MB.")
        return value
