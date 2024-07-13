from operator import mod
from rest_framework import generics, filters, permissions

from django_filters.rest_framework import DjangoFilterBackend

from referral import serializers, models, operations


# Create your views here.
class ReferralNetworkAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.ReferralNetworkSerializer
    filter_backends = [
        filters.OrderingFilter,
        DjangoFilterBackend,
        filters.SearchFilter,
    ]
    search_fields = ["username"]
    ordering_fields = "__all__"
    filterset_fields = "__all__"

    # Todo: apply cache to retrieve full network
    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return models.ReferralNetwork.objects.none()

        user_id = self.request.user.id
        operations.ReferralOperations().sp_referral_network(user_id)
        # if not search filter query param, return result from root user level
        if self.request.query_params.get("search") is None:
            return models.ReferralNetwork.objects.filter(
                referrer_id=user_id, network_type=models.ReferralNetwork.DOWNLINE
            )

        # Return all level
        return models.ReferralNetwork.objects.filter(
            network_type=models.ReferralNetwork.DOWNLINE
        )
