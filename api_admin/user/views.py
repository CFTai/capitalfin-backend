from django import conf

from rest_framework import generics, permissions, filters, response, status

from rest_framework_simplejwt import tokens

from django_filters.rest_framework import DjangoFilterBackend

from monolithic_api import pagination

from user import models, serializers as user_serializers
from api_admin.user import serializers


class AdminUserAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = serializers.AdminUserSerializer
    queryset = models.User.objects.filter(is_staff=False).all()
    pagination_class = pagination.PageNumberPagination
    filter_backends = [
        filters.OrderingFilter,
        filters.SearchFilter,
        DjangoFilterBackend,
    ]
    search_fields = ["username", "last_name", "first_name"]
    ordering_fields = "__all__"
    filterset_fields = "__all__"

    def post(self, request, *args, **kwargs):
        serializer = user_serializers.RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return response.Response(serializer.data, status=status.HTTP_200_OK)


class AdminUserDetailsAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = serializers.AdminUserSerializer
    queryset = models.User.objects.filter(is_staff=False).all()
    lookup_field = "pk"


class AdminUserSwitchAPIView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = serializers.AdminUserSerializer
    queryset = models.User.objects.filter(is_staff=False).all()
    lookup_field = "pk"

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        token = tokens.RefreshToken.for_user(instance)
        return response.Response(
            dict(
                switch=f"{conf.settings.USER_URL}/landing.html?access={str(token.access_token)}&refresh={str(token)}"
            )
        )
