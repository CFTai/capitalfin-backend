from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions, filters

from django_filters.rest_framework import DjangoFilterBackend

from account import serializers, models


# Create your views here.
class AccountAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.AccountSerializer
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = "__all__"
    filterset_fields = "__all__"

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return models.Account.objects.none()

        user_id = self.request.user.id
        return models.Account.objects.filter(user_id=user_id)


class AccountDetailsAPIView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.AccountSerializer
    lookup_field = "account_type_display"

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return models.Account.objects.none()

        user_id = self.request.user.id
        return models.Account.objects.filter(user_id=user_id)

    def get_object(self):
        queryset = self.get_queryset()
        url_param = self.kwargs.get("account_type_display")
        filtered_acc_type = next(
            filter(lambda type: type[1] == url_param, models.Account.ACCOUNT_TYPES),
            None,
        )

        filters = {}
        filters["account_type"] = filtered_acc_type[0]

        return get_object_or_404(queryset, **filters)
