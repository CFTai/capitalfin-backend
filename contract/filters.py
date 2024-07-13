from django_filters import rest_framework, BaseInFilter, NumberFilter

from contract.models import Contract


class NumberInFilter(BaseInFilter, NumberFilter):
    pass


class ContractFilter(rest_framework.FilterSet):
    contract_status_in = NumberInFilter("contract_status", lookup_expr="in")

    class Meta:
        model = Contract
        fields = "__all__"
