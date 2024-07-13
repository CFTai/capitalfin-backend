from rest_framework import generics, permissions, filters

from django_filters.rest_framework import DjangoFilterBackend

from monolithic_api import pagination

from api_admin.blockchain import serializers

from blockchain import models


class AdminBlockchainWalletAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = serializers.AdminBlockchainWalletSerializer
    queryset = models.BlockchainWallet.objects.all()
    pagination_class = pagination.PageNumberPagination
    filter_backends = [
        filters.OrderingFilter,
        filters.SearchFilter,
        DjangoFilterBackend,
    ]
    search_fields = ["user__username"]
    ordering_fields = "__all__"
    filterset_fields = "__all__"


class AdminBlockchainWalletDetailsAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = serializers.AdminBlockchainWalletSerializer
    queryset = models.BlockchainWallet.objects.all()
    lookup_field = "pk"
