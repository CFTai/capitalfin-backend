from django.db import transaction

from rest_framework import serializers

from api_admin.account import serializers as account_serializers

from api_admin.transaction import serializers as transaction_serializers

from withdrawal import models


class WithdrawalSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WithdrawalSettings
        fields = "__all__"


class WithdrawalBlockchainSerializer(serializers.ModelSerializer):
    account_details = account_serializers.AdminAccountSerializer(
        source="withdrawal_transaction.account", read_only=True
    )
    withdrawal_transaction = transaction_serializers.AdminTransactionSerializer()

    class Meta:
        model = models.WithdrawalBlockchain
        fields = "__all__"

    @transaction.atomic
    def update(self, instance, validated_data):
        withdrawal_transaction = validated_data.pop("withdrawal_transaction")
        db_withdrawal_transaction = instance.withdrawal_transaction
        db_withdrawal_transaction.transaction_status = withdrawal_transaction.get(
            "transaction_status", db_withdrawal_transaction.transaction_status
        )
        db_withdrawal_transaction.remark = withdrawal_transaction.get(
            "remark", db_withdrawal_transaction.remark
        )
        instance.withdrawal_transaction.save()
        return super().update(instance, validated_data)


class WithdrawalBankSerializer(serializers.ModelSerializer):
    account_details = account_serializers.AdminAccountSerializer(
        source="withdrawal_transaction.account", read_only=True
    )
    withdrawal_transaction = transaction_serializers.AdminTransactionSerializer()

    class Meta:
        model = models.WithdrawalBank
        fields = "__all__"

    @transaction.atomic
    def update(self, instance, validated_data):
        withdrawal_transaction = validated_data.pop("withdrawal_transaction")
        db_withdrawal_transaction = instance.withdrawal_transaction
        db_withdrawal_transaction.transaction_status = withdrawal_transaction.get(
            "transaction_status", db_withdrawal_transaction.transaction_status
        )
        db_withdrawal_transaction.remark = withdrawal_transaction.get(
            "remark", db_withdrawal_transaction.remark
        )
        instance.withdrawal_transaction.save()
        return super().update(instance, validated_data)
