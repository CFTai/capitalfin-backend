from rest_framework import serializers

from term import models


class AdminTermSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TermSettings
        fields = "__all__"


class AdminTermSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Term
        fields = "__all__"
