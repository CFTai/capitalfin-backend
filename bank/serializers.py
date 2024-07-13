from django.db import transaction
from django.contrib import auth

from rest_framework import serializers
from rest_framework.fields import empty

from bank import models


class BankSerializer(serializers.ModelSerializer):
    transaction_password = serializers.CharField(write_only=True)
    bank_status_display = serializers.ChoiceField(
        source="get_bank_status_display",
        choices=[i[1] for i in models.Bank.BANK_STATUS],
        read_only=True,
    )
    bank_status = serializers.IntegerField(read_only=True)
    remark = serializers.CharField(read_only=True)

    class Meta:
        model = models.Bank
        exclude = ["user"]

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        self.user = self.context["request"].user

    def validate_transaction_password(self, value):
        if auth.hashers.check_password(value, self.user.transaction_password) is False:
            raise serializers.ValidationError("Invalid password.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop("transaction_password")
        validated_data["user"] = self.context["request"].user
        return models.Bank.objects.create(**validated_data)
