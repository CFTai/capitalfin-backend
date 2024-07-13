from django.contrib import auth
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from rest_framework.fields import empty

from user import models as user_models
from account import models as account_models
from transaction import models as transaction_models
from term import models as term_models
from stake import models


class StakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Stake
        fields = "__all__"


class StakeQuoteSerializer(serializers.Serializer):
    amount = serializers.FloatField()
    share_percentage = serializers.FloatField(
        required=False,
        allow_null=True,
        help_text="only for member who has dividend invest share",
    )
    term = serializers.IntegerField()
    share_amount = serializers.SerializerMethodField()
    actual_amount = serializers.SerializerMethodField()

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        self.user = self.context["request"].user

    def get_share_amount(self, instance):
        return self.share_amount

    def get_actual_amount(self, instance):
        return self.actual_amount

    def validate_term(self, value):
        """
        Validate term
        - User can only have one ACTIVE term staked
        """
        self.term = term_models.Term.objects.filter(id=value).first()
        if self.term is None:
            raise serializers.ValidationError("Invalid terms.")

        stakes = models.Stake.objects.filter(
            user_id=self.user.id, stake_status=models.Stake.ACTIVE
        ).count()
        if stakes > 0:
            raise serializers.ValidationError("Stake still active.")
        return value

    def validate_share_percentage(self, value):
        self.share_rate = value / 100
        settings_type = term_models.TermSettings.SHARES_ALLOWANCE
        settings = term_models.TermSettings.objects.get(settings_type=settings_type)
        if self.share_rate > settings.value:
            raise serializers.ValidationError("Percentage exceed systems limit.")
        return value

    def validate_amount(self, value):
        settings_type = term_models.TermSettings.MINIMUM_AMOUNT
        settings = term_models.TermSettings.objects.get(settings_type=settings_type)
        if value < settings.value:
            raise serializers.ValidationError(
                "Amount must greater then systems minimum value."
            )

        settings_type = term_models.TermSettings.AMOUNT_MULTIPLE
        settings = term_models.TermSettings.objects.get(settings_type=settings_type)
        if value % settings.value != 0:
            raise serializers.ValidationError(
                f"Amount must multiple by {settings.value}"
            )

        self.credit_account = self.user.accounts.get(
            account_type=account_models.Account.CREDIT
        )
        if self.credit_account.is_enable is False:
            raise serializers.ValidationError("Account is not available.")

        self.actual_amount = value
        return value

    def validate(self, attrs):
        if hasattr(self, "share_rate") and self.share_rate is not None:
            self.share_amount = self.actual_amount * self.share_rate
            self.shares_account = self.user.accounts.get(
                account_type=account_models.Account.SHARES
            )
            if self.shares_account.available_balance < self.share_amount:
                raise serializers.ValidationError(
                    {"share_percentage": "Insufficient account balance."}
                )
            self.actual_amount = self.actual_amount - self.share_amount
        else:
            self.share_amount = 0

        if self.credit_account.available_balance < self.actual_amount:
            raise serializers.ValidationError(
                {"amount": "Insufficient account balance."}
            )

        if (
            self.user.is_active is False
            or self.user.status is not user_models.User.VERIFIED
        ):
            raise serializers.ValidationError(
                {"amount": "Current account status is not verified."}
            )
        return attrs


class StakePurchaseSerializer(StakeQuoteSerializer):
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
            transaction_type=transaction_models.Transaction.STAKE_PURCHASE_TRANSACTION,
        )
        if self.share_amount > 0:
            transaction_models.Transaction.objects.create(
                amount=self.share_amount * -1,
                account=self.shares_account,
                transaction_type=transaction_models.Transaction.STAKE_PURCHASE_TRANSACTION,
            )

        start_date = timezone.now()
        models.Stake.objects.create(
            amount=self.actual_amount,
            shares_amount=self.share_amount,
            total_amount=self.actual_amount + self.share_amount,
            available_amount=self.actual_amount + self.share_amount,
            start_date=start_date,
            end_date=start_date + timezone.timedelta(days=self.term.days),
            user=self.user,
            term=self.term,
            stake_status=models.Stake.ACTIVE,
        )
        return validated_data
