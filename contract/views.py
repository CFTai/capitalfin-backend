from rest_framework import generics, permissions, filters

from django_filters.rest_framework import DjangoFilterBackend

from monolithic_api import pagination

from contract import models, serializers, filters as contract_filters


# Create your views here.
class ContractAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.ContractSerializer
    queryset = models.Contract.objects.all()
    pagination_class = pagination.PageNumberPagination
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
        DjangoFilterBackend,
    ]
    search_fields = ["title", "code"]
    ordering_fields = "__all__"
    filterset_class = contract_filters.ContractFilter


class ContractDetailsAPIView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.ContractSerializer
    queryset = models.Contract.objects.exclude(
        contract_status__in=[models.Contract.INACTIVE, models.Contract.SUSPENDED]
    )
    lookup_field = "pk"
