from rest_framework import generics, permissions, filters

from django_filters.rest_framework import DjangoFilterBackend

from monolithic_api import pagination

from goldmine import models

from api_admin.goldmine import serializers


class AdminGoldmineBonusSettingsAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = serializers.AdminGoldmineBonusSettingsSerializer
    queryset = models.GoldmineBonusSettings.objects.all()
    pagination_class = pagination.PageNumberPagination
    filter_backends = [
        filters.OrderingFilter,
        DjangoFilterBackend,
    ]
    ordering_fields = "__all__"
    filterset_fields = "__all__"


class AdminGoldmineBonusSettingsDetailsAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = serializers.AdminGoldmineBonusSettingsSerializer
    queryset = models.GoldmineBonusSettings.objects.all()
    lookup_field = "pk"


class AdminGoldmineBonusTransactionAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = serializers.AdminGoldmineBonusTransactionSerializer
    queryset = models.GoldmineBonusTransaction.objects.all()
    pagination_class = pagination.PageNumberPagination
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
        DjangoFilterBackend,
    ]
    search_fields = ["user__username"]
    ordering_fields = "__all__"
    filterset_fields = "__all__"


class AdminGoldmineBonusTransactionDetailsAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = serializers.AdminGoldmineBonusTransactionSerializer
    queryset = models.GoldmineBonusTransaction.objects.all()
    lookup_field = "pk"
