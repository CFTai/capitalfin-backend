from rest_framework import generics, permissions, response, status

from user import serializers


# Create your views here.
class RegistrationAPIView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = serializers.RegistrationSerializer


class ProfileAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.UserSerializer

    def get_object(self):
        _user = self.request.user
        return _user


class PasswordAPIView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.PasswordSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(dict(message="success"), status=status.HTTP_200_OK)


class ForgetPasswordAPIView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = serializers.ForgetPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(dict(message="success"), status=status.HTTP_200_OK)


class ResetPasswordAPIView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = serializers.ResetPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(dict(message="success"), status=status.HTTP_200_OK)
