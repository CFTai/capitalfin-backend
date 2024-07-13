from rest_framework import generics, permissions, filters, response, status

from django_filters.rest_framework import DjangoFilterBackend

from monolithic_api import pagination

from invest import models, serializers, filters as invest_filters


# Create your views here.
class InvestQuoteAPIView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.InvestQuoteSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return response.Response(serializer.data, status=status.HTTP_200_OK)


class InvestAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.InvestSerializer
    pagination_class = pagination.PageNumberPagination
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
        DjangoFilterBackend,
    ]
    search_fields = ["contract__title", "contract__code"]
    ordering_fields = "__all__"
    filterset_class = invest_filters.InvestFilter

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return models.Invest.objects.none()
        return models.Invest.objects.filter(
            stake__user_id=self.request.user.id
        ).order_by("-start_date")

    def post(self, request, *args, **kwargs):
        serializer = serializers.InvestPurchaseSerializer(
            data=request.data, context={"request": self.request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data, status=status.HTTP_200_OK)


class InvestDetailsAPIView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.InvestSerializer
    lookup_field = "pk"

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return models.Invest.objects.none()
        return models.Invest.objects.filter(
            stake__user_id=self.request.user.id
        ).order_by("-start_date")
