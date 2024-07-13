from rest_framework import generics, permissions, filters

from django_filters.rest_framework import DjangoFilterBackend

from monolithic_api import pagination

from withdrawal import models

from api_admin.withdrawal import serializers, filters as withdrawal_filters


class AdminWithdrawalSettingsAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = serializers.WithdrawalSettingsSerializer
    queryset = models.WithdrawalSettings.objects.all()
    pagination_class = pagination.PageNumberPagination
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = "__all__"
    filterset_fields = "__all__"


class AdminWithdrawalSettingsDetailsAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = serializers.WithdrawalSettingsSerializer
    queryset = models.WithdrawalSettings.objects.all()
    lookup_field = "pk"


class AdminWithdrawalBlockchainAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = serializers.WithdrawalBlockchainSerializer
    queryset = models.WithdrawalBlockchain.objects.all()
    pagination_class = pagination.PageNumberPagination
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
        DjangoFilterBackend,
    ]
    search_fields = ["withdrawal_transaction__account__user__username"]
    ordering_fields = "__all__"
    filterset_class = withdrawal_filters.AdminWithdrawalBlockchainFilter


class AdminWithdrawalBlockchainDetailsAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = serializers.WithdrawalBlockchainSerializer
    queryset = models.WithdrawalBlockchain.objects.all()
    lookup_field = "pk"


class AdminWithdrawalBankAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = serializers.WithdrawalBankSerializer
    queryset = models.WithdrawalBank.objects.all()
    pagination_class = pagination.PageNumberPagination
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
        DjangoFilterBackend,
    ]
    search_fields = ["withdrawal_transaction__account__user__username"]
    ordering_fields = "__all__"
    filterset_class = withdrawal_filters.AdminWithdrawalBankFilter


class AdminWithdrawalBankDetailsAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = serializers.WithdrawalBankSerializer
    queryset = models.WithdrawalBank.objects.all()
    lookup_field = "pk"
