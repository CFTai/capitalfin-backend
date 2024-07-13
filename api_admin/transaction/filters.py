from django_filters import rest_framework

from transaction import models


class AdminTransactionFilter(rest_framework.FilterSet):
    account_type = rest_framework.NumberFilter("account__account_type")

    class Meta:
        model = models.Transaction
        fields = "__all__"
