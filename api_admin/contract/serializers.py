from rest_framework import serializers

from contract import models


class AdminContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Contract
        fields = "__all__"
