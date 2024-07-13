from django_filters import rest_framework

from invest import models


class InvestFilter(rest_framework.FilterSet):
    contract_title = rest_framework.CharFilter(
        field_name="contract__title", lookup_expr="icontains"
    )
    contract_code = rest_framework.CharFilter(
        field_name="contract__code", lookup_expr="icontains"
    )
    start_date = rest_framework.DateFromToRangeFilter(field_name="start_date")

    class Meta:
        model = models.Invest
        fields = "__all__"
