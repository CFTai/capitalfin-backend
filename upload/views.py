from rest_framework import generics, permissions, parsers

from . import serializers


# Create your views here.
class UploadAPIView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    serializer_class = serializers.UploadSerializer
