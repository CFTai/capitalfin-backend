from django_filters import rest_framework

from withdrawal import models


class AdminWithdrawalBlockchainFilter(rest_framework.FilterSet):
    withdrawal_status = rest_framework.NumberFilter(
        "withdrawal_transaction__transaction_status"
    )
    withdrawal_date = rest_framework.DateFromToRangeFilter(field_name="withdrawal_date")

    class Meta:
        model = models.WithdrawalBlockchain
        fields = "__all__"


class AdminWithdrawalBankFilter(rest_framework.FilterSet):
    withdrawal_status = rest_framework.NumberFilter(
        "withdrawal_transaction__transaction_status"
    )
    withdrawal_date = rest_framework.DateFromToRangeFilter(field_name="withdrawal_date")

    class Meta:
        model = models.WithdrawalBank
        fields = "__all__"
