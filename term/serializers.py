from rest_framework import serializers

from term import models


class TermSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Term
        fields = "__all__"
