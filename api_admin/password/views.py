from rest_framework import generics, permissions

from user import models
from api_admin.password import serializers


class AdminPasswordDetailsAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = serializers.AdminPasswordSerializer
    queryset = models.User.objects.filter(is_staff=False).all()
    lookup_field = "pk"
