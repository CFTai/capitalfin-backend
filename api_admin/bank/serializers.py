from rest_framework import serializers

from bank import models


class AdminBankSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Bank
        fields = "__all__"
