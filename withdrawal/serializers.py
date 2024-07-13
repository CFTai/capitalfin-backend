from django.contrib import auth
from django.db import transaction

from rest_framework import serializers
from rest_framework.fields import empty

from user import models as user_models

from blockchain import models as blockchain_models

from bank import models as bank_models

from account import models as account_models

from transaction import models as transaction_models

from withdrawal.const import (
    WITHDRAWAL_ACCOUNTS,
    WITHDRAWAL_METHODS,
    WITHDRAWAL_BLOCKCHAIN,
    WITHDRAWAL_BANK,
)
from withdrawal import models


class WithdrawalQuoteSerializer(serializers.Serializer):
    account = serializers.ChoiceField(
        write_only=True,
        choices=[
            i[1]
            for i in account_models.Account.ACCOUNT_TYPES
            if i[0] in WITHDRAWAL_ACCOUNTS
        ],
    )
    amount = serializers.FloatField()
    service_fee = serializers.SerializerMethodField()
    gas_fee = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    method = serializers.ChoiceField(
        choices=WITHDRAWAL_METHODS, default=WITHDRAWAL_BLOCKCHAIN
    )

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        self.user = self.context["request"].user

    def get_total_amount(self, instance):
        return self.total_amount

    def get_service_fee(self, instance):
        return self.service_fee

    def get_gas_fee(self, instance):
        return self.gas_fee

    def validate_account(self, value):
        account_type = next(
            filter(lambda type: type[1] == value, account_models.Account.ACCOUNT_TYPES),
            None,
        )
        self.account = account_models.Account.objects.get(
            user=self.user, account_type=account_type[0]
        )
        if self.account.is_enable is False or self.account.is_withdrawable is False:
            raise serializers.ValidationError(
                "Account is not available for withdrawal."
            )
        return value

    def validate(self, attrs):
        if (
            self.user.is_active is False
            or self.user.status is not user_models.User.VERIFIED
        ):
            raise serializers.ValidationError(
                {"amount": "Current account status is not verified."}
            )

        if attrs["method"] == WITHDRAWAL_BLOCKCHAIN:
            self.withdrawal_details = blockchain_models.BlockchainWallet.objects.filter(
                wallet_type=blockchain_models.BlockchainWallet.WITHDRAWAL,
                wallet_status=blockchain_models.BlockchainWallet.AUTHORIZED,
                user=self.user,
            ).first()
            if self.withdrawal_details is None:
                raise serializers.ValidationError(
                    {"amount": "Withdrawal method has not been authorized."}
                )

            self.service_fee = models.WithdrawalSettings.objects.get(
                settings_type=models.WithdrawalSettings.BLOCKCHAIN_SERVICE_FEE
            )
            self.gas_fee = models.WithdrawalSettings.objects.get(
                settings_type=models.WithdrawalSettings.BLOCKCHAIN_GAS_FEE
            )
            self.min_withdraw = models.WithdrawalSettings.objects.get(
                settings_type=models.WithdrawalSettings.BLOCKCHAIN_MINIMUM_WITHDRAW
            )
        elif attrs["method"] == WITHDRAWAL_BANK:
            self.withdrawal_details = bank_models.Bank.objects.filter(
                bank_status=bank_models.Bank.AUTHORIZED,
                user=self.user,
            ).first()
            if self.withdrawal_details is None:
                raise serializers.ValidationError(
                    {"amount": "Withdrawal method has not been authorized."}
                )

            self.service_fee = models.WithdrawalSettings.objects.get(
                settings_type=models.WithdrawalSettings.BANK_SERVICE_FEE
            )
            self.min_withdraw = models.WithdrawalSettings.objects.get(
                settings_type=models.WithdrawalSettings.BANK_MINIMUM_WITHDRAW
            )

        self.amount = attrs["amount"]
        if self.amount > self.account.available_balance:
            raise serializers.ValidationError(
                {"amount": "Insufficient account balance."}
            )

        if self.amount < self.min_withdraw.rate:
            raise serializers.ValidationError(
                {
                    "amount": "Withdrawal amount must greater then systems minimum values."
                }
            )

        multiple = models.WithdrawalSettings.objects.get(
            settings_type=models.WithdrawalSettings.WITHDRAW_MULTIPLE
        )
        if self.amount % multiple.rate != 0:
            raise serializers.ValidationError(
                {"amount": f"Withdrawal amount must multiple by {multiple.rate}"}
            )

        self.service_fee = self.amount * self.service_fee.rate
        self.gas_fee = (
            self.gas_fee.rate if attrs["method"] == WITHDRAWAL_BLOCKCHAIN else 0
        )
        self.total_amount = self.amount - self.service_fee - self.gas_fee

        return attrs


class WithdrawalSerializer(WithdrawalQuoteSerializer):
    transaction_password = serializers.CharField(write_only=True)

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        self.user = self.context["request"].user

    def validate_transaction_password(self, value):
        if auth.hashers.check_password(value, self.user.transaction_password) is False:
            raise serializers.ValidationError("Invalid password.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop("transaction_password")

        withdrawal_tx = transaction_models.Transaction.objects.create(
            amount=self.total_amount * -1,
            account=self.account,
            transaction_type=transaction_models.Transaction.WITHDRAWAL_TRANSACTION,
            transaction_status=transaction_models.Transaction.PENDING,
        )
        service_fee_tx = transaction_models.Transaction.objects.create(
            amount=self.service_fee * -1,
            account=self.account,
            transaction_type=transaction_models.Transaction.WITHDRAWAL_FEE,
        )
        if validated_data["method"] == WITHDRAWAL_BLOCKCHAIN:
            gas_fee_tx = transaction_models.Transaction.objects.create(
                amount=self.gas_fee * -1,
                account=self.account,
                transaction_type=transaction_models.Transaction.WITHDRAWAL_FEE,
                remark="Gas fee",
            )
            models.WithdrawalBlockchain.objects.create(
                wallet_address=self.withdrawal_details.wallet_address,
                withdrawal_transaction=withdrawal_tx,
                service_fee_transaction=service_fee_tx,
                gas_fee_transaction=gas_fee_tx,
            )
        elif validated_data["method"] == WITHDRAWAL_BANK:
            models.WithdrawalBank.objects.create(
                account_name=self.withdrawal_details.account_name,
                account_number=self.withdrawal_details.account_number,
                bank_name=self.withdrawal_details.bank_name,
                bank_country=self.withdrawal_details.bank_country,
                bank_region=self.withdrawal_details.bank_region,
                bank_branch=self.withdrawal_details.bank_branch,
                withdrawal_transaction=withdrawal_tx,
                service_fee_transaction=service_fee_tx,
            )

        return object
