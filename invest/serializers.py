from django.contrib import auth
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from rest_framework.fields import empty

from account import models as account_models
from transaction import models as transaction_models
from stake import models as stake_models
from contract import models as contract_models
from referral import tasks as referral_tasks
from invest import models


class InvestSerializer(serializers.ModelSerializer):
    contract_code = serializers.CharField(source="contract.code", read_only=True)
    contract_title = serializers.CharField(source="contract.title", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = models.Invest
        fields = "__all__"


class InvestQuoteSerializer(serializers.Serializer):
    amount = serializers.FloatField()
    share_percentage = serializers.FloatField(
        required=False,
        allow_null=True,
        help_text="only for member who has dividend invest share",
    )
    contract = serializers.IntegerField()
    share_amount = serializers.SerializerMethodField()
    actual_amount = serializers.SerializerMethodField()

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        self.user = self.context["request"].user
        self.stake = stake_models.Stake.objects.filter(
            user=self.user, stake_status=stake_models.Stake.ACTIVE
        ).first()
        self.contract = None
        self.share_rate = None
        self.share_amount = 0

    def get_share_amount(self, instance):
        return self.share_amount

    def get_actual_amount(self, instance):
        return self.actual_amount

    def validate_contract(self, value):
        # Contract that is investing must be OPEN status
        self.contract = contract_models.Contract.objects.filter(
            contract_status=contract_models.Contract.OPEN, id=value
        ).first()
        if self.contract is None:
            raise serializers.ValidationError("Invalid contract.")
        return value

    def validate_amount(self, value):
        self.actual_amount = value
        return value

    def validate_share_percentage(self, value):
        self.share_rate = value / 100
        return value

    def validate(self, attrs):
        """
        Validate of multiple criteria.
            Check stake/master contract activated.
            Check investing amount is met with minimum amount, and amount block/multiple requirement of contract.
            Verify share allowance with contract that is investing.
            Check credit(USDT) and shares account balance availability.
        """
        # Check master contract/stake
        if self.stake is None:
            raise serializers.ValidationError({"contract": "Ineligible to invest."})

        # Check minimum amount
        if self.actual_amount < self.contract.minimum_amount:
            raise serializers.ValidationError(
                {
                    "amount": f"Amount must greater then contract minimum amount {self.contract.minimum_amount}."
                }
            )

        # amount multiple
        if self.actual_amount % self.contract.amount_multiple != 0:
            raise serializers.ValidationError(
                {"amount": f"Amount must multiple by {self.contract.amount_multiple}"}
            )

        # share allowance rate
        if self.share_rate and self.share_rate > self.contract.share_allowance_rate:
            raise serializers.ValidationError(
                {"share_percentage": "Percentage exceed systems limit."}
            )

        # share balance
        if self.share_rate:
            self.share_amount = self.actual_amount * self.share_rate
            self.shares_account = self.user.accounts.get(
                account_type=account_models.Account.SHARES
            )
            if self.shares_account.available_balance < self.share_amount:
                raise serializers.ValidationError(
                    {"share_percentage": "Insufficient account balance."}
                )
            self.actual_amount = self.actual_amount - self.share_amount

        # account balance
        self.credit_account = self.user.accounts.get(
            account_type=account_models.Account.CREDIT
        )
        if self.credit_account.is_enable is False:
            raise serializers.ValidationError({"amount": "Account is not available."})
        if self.credit_account.available_balance < self.actual_amount:
            raise serializers.ValidationError(
                {"amount": "Insufficient account balance."}
            )
        return attrs


class InvestPurchaseSerializer(InvestQuoteSerializer):
    transaction_password = serializers.CharField(write_only=True)

    def validate_transaction_password(self, value):
        if auth.hashers.check_password(value, self.user.transaction_password) is False:
            raise serializers.ValidationError("Invalid password.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop("transaction_password")

        transaction_models.Transaction.objects.create(
            amount=self.actual_amount * -1,
            account=self.credit_account,
            transaction_type=transaction_models.Transaction.INVEST_TRANSACTION,
        )
        if self.share_amount > 0:
            transaction_models.Transaction.objects.create(
                amount=self.share_amount * -1,
                account=self.shares_account,
                transaction_type=transaction_models.Transaction.INVEST_TRANSACTION,
            )

        start_date = timezone.now()
        models.Invest.objects.create(
            amount=self.actual_amount,
            shares_amount=self.share_amount,
            total_amount=self.actual_amount + self.share_amount,
            bonus_income_cap=(self.actual_amount + self.share_amount)
            * self.contract.bonus_income_cap_rate,
            start_date=start_date,
            end_date=start_date + timezone.timedelta(days=self.contract.term.days),
            contract=self.contract,
            stake=self.stake,
        )

        referral_tasks.referral_bonus_calculator(
            self.user.id, self.contract.term.id, self.actual_amount
        )

        return validated_data
