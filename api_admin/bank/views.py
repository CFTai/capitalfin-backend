from rest_framework import permissions, generics, filters

from django_filters.rest_framework import DjangoFilterBackend

from monolithic_api import pagination

from api_admin.bank import serializers

from bank import models


class AdminBankAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = serializers.AdminBankSerializer
    queryset = models.Bank.objects.all()
    pagination_class = pagination.PageNumberPagination
    filter_backends = [
        filters.OrderingFilter,
        filters.SearchFilter,
        DjangoFilterBackend,
    ]
    search_fields = ["user__username"]
    ordering_fields = "__all__"
    filterset_fields = "__all__"


class AdminBankDetailsAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = serializers.AdminBankSerializer
    queryset = serializers.models.Bank.objects.all()
    lookup_field = "pk"
