from rest_framework import generics, filters, permissions

from django_filters.rest_framework import DjangoFilterBackend

from monolithic_api import pagination

from transaction import models

from api_admin.transaction import serializers, filters as transaction_filters


class AdminTransactionAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = serializers.AdminTransactionSerializer
    queryset = models.Transaction.objects.all()
    pagination_class = pagination.PageNumberPagination
    filter_backends = [
        filters.OrderingFilter,
        filters.SearchFilter,
        DjangoFilterBackend,
    ]
    search_fields = ["account__user__username"]
    ordering_fields = "__all__"
    filterset_class = transaction_filters.AdminTransactionFilter


class AdminTransactionDetailsAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = serializers.AdminTransactionSerializer
    queryset = models.Transaction.objects.all()
    lookup_field = "pk"
