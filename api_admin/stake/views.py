from rest_framework import generics, permissions, filters

from django_filters.rest_framework import DjangoFilterBackend

from monolithic_api import pagination

from stake import models

from api_admin.stake import serializers


class AdminStakeAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = serializers.AdminStakeSerializer
    queryset = models.Stake.objects.all()
    pagination_class = pagination.PageNumberPagination
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
        DjangoFilterBackend,
    ]
    search_fields = ["user__username"]
    ordering_fields = "__all__"
    filterset_fields = "__all__"


class AdminStakeDetailsAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = serializers.AdminStakeSerializer
    queryset = models.Stake.objects.all()
    lookup_field = "pk"
