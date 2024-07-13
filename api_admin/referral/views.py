from rest_framework import generics, filters, permissions

from django_filters.rest_framework import DjangoFilterBackend

from monolithic_api import pagination

from referral import models

from api_admin.referral import serializers


class AdminReferralAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = serializers.AdminReferralSerializer
    queryset = models.Referral.objects.all()
    pagination_class = pagination.PageNumberPagination
    filter_backends = [
        filters.OrderingFilter,
        filters.SearchFilter,
        DjangoFilterBackend,
    ]
    search_fields = ["referrer__username", "referred__username"]
    ordering_fields = "__all__"
    filterset_fields = "__all__"


class AdminReferralDetailsAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = serializers.AdminReferralSerializer
    queryset = models.Referral.objects.all()
    lookup_field = "pk"


class AdminReferralBonusSettingsAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = serializers.AdminReferralBonusSettingsSerializer
    queryset = models.ReferralBonusSettings.objects.all()
    pagination_class = pagination.PageNumberPagination
    filter_backends = [
        filters.OrderingFilter,
        # filters.SearchFilter,
        DjangoFilterBackend,
    ]
    # search_fields = []
    ordering_fields = "__all__"
    filterset_fields = "__all__"


class AdminReferralBonusSettingsDetailsAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = serializers.AdminReferralBonusSettingsSerializer
    queryset = models.ReferralBonusSettings.objects.all()
    lookup_field = "pk"


class AdminReferralBonusTransactionAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = serializers.AdminReferralBonusTransactionSerializer
    queryset = models.ReferralBonusTransaction.objects.all()
    pagination_class = pagination.PageNumberPagination
    filter_backends = [
        filters.OrderingFilter,
        filters.SearchFilter,
        DjangoFilterBackend,
    ]
    search_fields = ["user__username", "referrer__username", "term__title"]
    ordering_fields = "__all__"
    filterset_fields = "__all__"


class AdminReferralBonusTransactionDetailsAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = serializers.AdminReferralBonusTransactionSerializer
    queryset = models.ReferralBonusTransaction.objects.all()
    lookup_field = "pk"
