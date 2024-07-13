from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions, response, status

from stake import serializers, models


# Create your views here.
class StakeQuoteAPIView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.StakeQuoteSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return response.Response(serializer.data, status=status.HTTP_200_OK)


class StakeAPIView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.StakePurchaseSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data, status=status.HTTP_200_OK)


class StakeDetailsAPIView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.StakeSerializer
    lookup_field = "stake_status"

    def get_queryset(self):
        return models.Stake.objects.filter(user=self.request.user)

    def get_object(self):
        queryset = self.get_queryset()
        url_param = self.kwargs["stake_status"]
        filtered_status = next(
            filter(lambda type: type[1] == url_param, models.Stake.STAKE_STATUS),
            None,
        )
        filters = {}
        filters["stake_status"] = filtered_status[0]

        return get_object_or_404(queryset, **filters)
