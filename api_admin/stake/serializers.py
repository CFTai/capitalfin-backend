from rest_framework import serializers

from stake import models


class AdminStakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Stake
        fields = "__all__"
