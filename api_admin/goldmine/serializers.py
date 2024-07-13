from rest_framework import serializers

from goldmine import models


class AdminGoldmineBonusSettingsSerializer(serializers.ModelSerializer):
    term_title = serializers.CharField(source="term.title", read_only=True)

    class Meta:
        model = models.GoldmineBonusSettings
        fields = "__all__"


class AdminGoldmineBonusTransactionSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = models.GoldmineBonusTransaction
        fields = "__all__"
