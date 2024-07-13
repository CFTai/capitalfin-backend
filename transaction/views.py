from rest_framework import generics, permissions, filters

from django_filters.rest_framework import DjangoFilterBackend

from monolithic_api import pagination

from transaction import serializers, filters as transaction_filters


# Create your views here.
class TransactionAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.TransactionSerializer
    pagination_class = pagination.PageNumberPagination
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = "__all__"
    filterset_class = transaction_filters.TransactionFilter

    def get_queryset(self):
        return serializers.models.Transaction.objects.filter(
            account__user_id=self.request.user.id
        )


class TransactionDetailsAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.TransactionSerializer
    lookup_field = "pk"

    def get_queryset(self):
        return serializers.models.Transaction.objects.filter(
            account__user_id=self.request.user.id
        )
