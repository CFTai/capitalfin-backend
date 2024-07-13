from rest_framework import generics, permissions, filters

from django_filters.rest_framework import DjangoFilterBackend

from monolithic_api import pagination

from term import models

from api_admin.term import serializers


class AdminTermSettingsAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = serializers.AdminTermSettingsSerializer
    queryset = models.TermSettings.objects.all()
    pagination_class = pagination.PageNumberPagination
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = "__all__"
    ordering_fields = "__all__"


class AdminTermSettingsDetailsAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = serializers.AdminTermSettingsSerializer
    queryset = models.TermSettings.objects.all()


class AdminTermAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = serializers.AdminTermSerializer
    queryset = models.Term.objects.all()
    pagination_class = pagination.PageNumberPagination
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = "__all__"
    ordering_fields = "__all__"


class AdminTermDetailsAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = serializers.AdminTermSerializer
    queryset = models.Term.objects.all()
