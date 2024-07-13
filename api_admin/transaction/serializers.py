from django.db import transaction

from rest_framework import serializers

from account import models as account_models

from transaction import models


class AdminTransactionSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="account.user.id", read_only=True)
    account_type = serializers.IntegerField(
        source="account.account_type", read_only=True
    )

    class Meta:
        model = models.Transaction
        fields = "__all__"

    @transaction.atomic
    def create(self, validated_data):
        transaction = models.Transaction.objects.create(**validated_data)
        return transaction

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.transaction_status = validated_data.get("transaction_status")
        instance.remark = validated_data.get("remark", None)
        instance.save()
        return instance
