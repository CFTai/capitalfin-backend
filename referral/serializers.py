from rest_framework import serializers

from referral import models


class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class ReferralNetworkSerializer(serializers.ModelSerializer):
    referred_users = RecursiveField(many=True)

    class Meta:
        model = models.ReferralNetwork
        fields = "__all__"
