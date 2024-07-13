from rest_framework import generics, permissions, filters

from django_filters.rest_framework import DjangoFilterBackend

from monolithic_api import pagination

from contract import models

from api_admin.contract import serializers


class AdminContractAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = serializers.AdminContractSerializer
    queryset = models.Contract.objects.all()
    pagination_class = pagination.PageNumberPagination
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
        DjangoFilterBackend,
    ]
    filterset_fields = "__all__"
    ordering_fields = "__all__"
    search_fields = ["title", "code"]


class AdminContractDetailsAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = serializers.AdminContractSerializer
    queryset = models.Contract.objects.all()
    lookup_field = "pk"
