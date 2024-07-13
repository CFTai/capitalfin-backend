from rest_framework import generics, permissions, filters

from django_filters.rest_framework import DjangoFilterBackend

from monolithic_api import pagination

from term import serializers, models


# Create your views here.
class TermAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.TermSerializer
    pagination_class = pagination.PageNumberPagination
    queryset = models.Term.objects.all()
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
        DjangoFilterBackend,
    ]
    search_fields = ["title"]
    ordering_fields = "__all__"
    filterset_fields = "__all__"


class TermDetailsAPIView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.TermSerializer
    queryset = models.Term.objects.all()
    lookup_field = "pk"
