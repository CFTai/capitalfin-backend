from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions, response, status

from monolithic_api import pagination

from blockchain import serializers, models


# Create your views here.
class BlockchainWalletAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.BlockchainWalletSerializer
    pagination_class = pagination.PageNumberPagination

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return models.BlockchainWallet.objects.none()
        return models.BlockchainWallet.objects.filter(
            user_id=self.request.user.id
        ).order_by("-date_created")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data, status=status.HTTP_200_OK)


class BlockchainWalletDetailsAPIView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.BlockchainWalletSerializer
    lookup_field = "wallet_status"

    def get_queryset(self):
        return models.BlockchainWallet.objects.filter(user_id=self.request.user.id)

    def get_object(self):
        queryset = self.get_queryset()
        url_param = self.kwargs["wallet_status"]
        filtered_status = next(
            filter(
                lambda type: type[1] == url_param, models.BlockchainWallet.WALLET_STATUS
            ),
            None,
        )
        filters = {}
        filters["wallet_status"] = filtered_status[0]
        return get_object_or_404(queryset, **filters)
