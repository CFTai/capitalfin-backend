from rest_framework import serializers

from account import models, serializers as account_serializers


class AdminAccountSerializer(account_serializers.AccountSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = models.Account
        fields = "__all__"
