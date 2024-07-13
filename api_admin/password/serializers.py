from django.contrib import auth
from django.core import exceptions
from django.db import transaction

from rest_framework import serializers

from user import models as user_models


class AdminPasswordSerializer(serializers.ModelSerializer):
    encrypted_password = None
    encrypted_transaction_password = None

    password = serializers.CharField(write_only=True)
    transaction_password = serializers.CharField(write_only=True)

    class Meta:
        model = user_models.User
        fields = ["username", "id", "password", "transaction_password"]

    def validate_password(self, value):
        try:
            auth.password_validation.validate_password(value)
            self.encrypted_password = auth.hashers.make_password(value)
            return value
        except exceptions.ValidationError as error:
            raise serializers.ValidationError(
                "Use 8 or more characters with a mix of letters, numbers & symbols"
            )

    def validate_transaction_password(self, value):
        try:
            auth.password_validation.validate_password(value)
            self.encrypted_transaction_password = auth.hashers.make_password(value)
            return value
        except exceptions.ValidationError as error:
            raise serializers.ValidationError(
                "Use 8 or more characters with a mix of letters, numbers & symbols"
            )

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.password = self.encrypted_password
        instance.transaction_password = self.encrypted_transaction_password
        instance.save(update_fields=["password", "transaction_password"])
        return instance
