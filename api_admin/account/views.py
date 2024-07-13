from rest_framework import generics, permissions, filters

from django_filters.rest_framework import DjangoFilterBackend

from monolithic_api import pagination

from account import models

from api_admin.account import serializers


class AdminAccountAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = serializers.AdminAccountSerializer
    queryset = models.Account.objects.all()
    pagination_class = pagination.PageNumberPagination
    filter_backends = [
        filters.OrderingFilter,
        filters.SearchFilter,
        DjangoFilterBackend,
    ]
    search_fields = ["user__username"]
    ordering_fields = "__all__"
    filterset_fields = "__all__"


class AdminAccountDetailsAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = serializers.AdminAccountSerializer
    queryset = models.Account.objects.all()
    lookup_field = "pk"
