from django_filters import rest_framework

from transaction import models


class TransactionFilter(rest_framework.FilterSet):
    account_type = rest_framework.NumberFilter(field_name="account__account_type")
    transaction_date = rest_framework.DateFromToRangeFilter(
        field_name="transaction_date"
    )

    class Meta:
        model = models.Transaction
        fields = "__all__"
