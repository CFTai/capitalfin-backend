from django.contrib import auth
from django.db import transaction

from rest_framework import serializers
from rest_framework.fields import empty

from blockchain import models


class BlockchainWalletSerializer(serializers.ModelSerializer):
    transaction_password = serializers.CharField(write_only=True)
    wallet_status_display = serializers.CharField(
        source="get_wallet_status_display",
        read_only=True,
    )

    class Meta:
        model = models.BlockchainWallet
        exclude = ["user", "wallet_type"]

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
        validated_data["user"] = self.user

        wallet = models.BlockchainWallet.objects.create(**validated_data)
        return wallet
