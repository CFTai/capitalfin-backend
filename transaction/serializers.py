from django.db import transaction

from rest_framework import serializers

from transaction import models


class TransactionSerializer(serializers.ModelSerializer):
    account_type_display = serializers.CharField(
        source="account.get_account_type_display", read_only=True
    )
    transaction_type_display = serializers.CharField(
        source="get_transaction_type_display", read_only=True
    )
    transaction_status_display = serializers.CharField(
        source="get_transaction_status_display", read_only=True
    )

    class Meta:
        model = models.Transaction
        fields = "__all__"

    def validate_transaction_status(self, value):
        # Only VOID is allow else will have exception
        if value != models.Transaction.VOIDED:
            raise serializers.ValidationError("Invalid status")
        return value

    def validate(self, attrs):
        # Only Withdrawal transaction can be updated by user else will have exception
        if self.instance.transaction_type != models.Transaction.WITHDRAWAL_TRANSACTION:
            raise serializers.ValidationError({"id": "Transaction is not editable."})
        return super().validate(attrs)

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.transaction_status = validated_data["transaction_status"]
        instance.save()
        return instance
