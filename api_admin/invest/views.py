from rest_framework import generics, permissions, filters

from django_filters.rest_framework import DjangoFilterBackend

from monolithic_api import pagination

from invest import models

from api_admin.invest import serializers


class AdminInvestAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = serializers.AdminInvestSerializer
    queryset = models.Invest.objects.all()
    pagination_class = pagination.PageNumberPagination
    filter_backends = [
        filters.OrderingFilter,
        filters.SearchFilter,
        DjangoFilterBackend,
    ]
    search_fields = ["contract__title", "contract__code", "stake__user__username"]
    ordering_fields = "__all__"
    filterset_fields = "__all__"


class AdminInvestDetailsAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = serializers.AdminInvestSerializer
    queryset = models.Invest.objects.all()
    lookup_field = "pk"


class AdminInvestBonusTransactionAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = serializers.AdminInvestBonusTransactionSerializer
    queryset = models.InvestBonusTransaction.objects.all()
    pagination_class = pagination.PageNumberPagination
    filter_backends = [
        filters.OrderingFilter,
        filters.SearchFilter,
        DjangoFilterBackend,
    ]
    search_fields = [
        "invest__stake__user__username",
        "invest__contract__title",
        "invest__contract__code",
    ]
    ordering_fields = "__all__"
    filterset_fields = "__all__"


class AdminInvestBonusTransactionDetailsAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = serializers.AdminInvestBonusTransactionSerializer
    queryset = models.InvestBonusTransaction.objects.all()
    lookup_field = "pk"
