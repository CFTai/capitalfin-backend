from django import utils
from django.core import exceptions
from django.contrib import auth
from django.db import transaction

from rest_framework import serializers
from rest_framework.fields import empty

from referral import tasks as referral_tasks

from user import models, helpers, tasks


class RegistrationSerializer(serializers.ModelSerializer):
    referrer = None

    username = serializers.CharField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    password = serializers.CharField(write_only=True)
    transaction_password = serializers.CharField(write_only=True)
    referrer_username = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )

    class Meta:
        model = models.User
        exclude = [
            "fullname_pinyin",
            "user_permissions",
            "groups",
            "remark",
            "status",
            "last_login",
            "is_active",
            "is_staff",
            "is_superuser",
        ]

    def validate_username(self, value):
        if models.User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def validate_email(self, value):
        user = models.User.objects.filter(email=value).first()
        if not user is None:
            raise serializers.ValidationError("Email is already exit")
        return value

    def validate_password(self, value):
        try:
            auth.password_validation.validate_password(value)
            self.encrypted_password = auth.hashers.make_password(value)
            return value
        except exceptions.ValidationError as error:
            raise serializers.ValidationError(
                "Use 8 or more characters with a mix of letters, numbers & symbols"
            )

    def validate_transaction_password(self, value):
        try:
            auth.password_validation.validate_password(value)
            self.encrypted_transaction_password = auth.hashers.make_password(value)
            return value
        except exceptions.ValidationError as error:
            raise serializers.ValidationError(
                "Use 8 or more characters with a mix of letters, numbers & symbols"
            )

    def validate_referrer_username(self, value):
        self.referrer = models.User.objects.filter(
            username=value, is_active=True
        ).first()
        if self.referrer is None:
            raise serializers.ValidationError("Invalid referrer")
        return value

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop("referrer_username", None)

        # validated_data["username"] = helpers.generate_member_number()
        validated_data["password"] = self.encrypted_password
        validated_data["transaction_password"] = self.encrypted_transaction_password
        user = super().create(validated_data)

        if self.referrer is not None:
            referral_tasks.referral_registered.delay(self.referrer.id, user.id)

        tasks.email_welcome_message.delay(user.username, user.email)
        return user


class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserDetails
        exclude = ["user"]


class UserContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserContact
        exclude = ["user"]


class UserAttachmentSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="upload.file_data.name", read_only=True)
    url = serializers.CharField(source="upload.file_data.url", read_only=True)

    class Meta:
        model = models.UserAttachments
        exclude = ["user", "id"]


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(read_only=True)
    details = UserDetailsSerializer()
    contact = UserContactSerializer()
    attachments = UserAttachmentSerializer(many=True)
    status = serializers.ChoiceField(
        read_only=True, choices=[i[0] for i in models.User.USER_STATUS]
    )
    status_display = serializers.ChoiceField(
        source="get_status_display",
        read_only=True,
        choices=[i[1] for i in models.User.USER_STATUS],
    )
    email = serializers.EmailField(read_only=True)

    class Meta:
        model = models.User
        exclude = [
            "user_permissions",
            "groups",
            "last_login",
            "is_active",
            "is_staff",
            "is_superuser",
            "password",
            "transaction_password",
        ]

    @transaction.atomic
    def update(self, instance, validated_data):
        details = validated_data.pop("details", None)
        if not details is None:
            sub_instance = (
                instance.details
                if hasattr(instance, "details")
                else models.UserDetails(user=instance)
            )
            serialized = UserDetailsSerializer(instance=sub_instance, data=details)
            serialized.is_valid(raise_exception=True)
            serialized.save()

        attachments = validated_data.pop("attachments", None)
        if not attachments is None:
            for i in attachments:
                models.UserAttachments.objects.create(
                    user=instance, upload=i.get("upload", None)
                )

        contact = validated_data.pop("contact", None)
        if not contact is None:
            sub_instance = (
                instance.contact
                if hasattr(instance, "contact")
                else models.UserContact(user=instance)
            )
            serialized = UserContactSerializer(instance=sub_instance, data=contact)
            serialized.is_valid(raise_exception=True)
            serialized.save()

        validated_data["status"] = models.User.PENDING
        return super().update(instance, validated_data)


class PasswordSerializer(serializers.Serializer):
    password_type = serializers.ChoiceField(
        choices=["login", "transaction"], write_only=True
    )
    current_password = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        self.user = self.context["request"].user

    def validate_password(self, value):
        try:
            auth.password_validation.validate_password(value)
            self.encrypted_password = auth.hashers.make_password(value)
            return value
        except exceptions.ValidationError as error:
            raise serializers.ValidationError(
                "Use 8 or more characters with a mix of letters, numbers & symbols"
            )

    def validate(self, data):
        current_password = data.get("current_password", None)
        if (
            data["password_type"] == "login"
            and auth.hashers.check_password(current_password, self.user.password)
            is False
        ):
            raise serializers.ValidationError(
                dict(current_password="Invalid password.")
            )
        elif (
            data["password_type"] == "transaction"
            and auth.hashers.check_password(
                current_password, self.user.transaction_password
            )
            is False
        ):
            raise serializers.ValidationError(
                dict(current_password="Invalid password.")
            )

        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                dict(confirm_password="Password mismatch.")
            )
        return data

    @transaction.atomic
    def create(self, validated_data):
        if validated_data["password_type"] == "login":
            self.user.password = self.encrypted_password
            self.user.save(update_fields=["password"])
        elif validated_data["password_type"] == "transaction":
            self.user.transaction_password = self.encrypted_password
            self.user.save(update_fields=["transaction_password"])
        return validated_data


class ForgetPasswordSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True)

    def validate_username(self, value):
        self.user = models.User.objects.filter(username=value).first()
        if self.user is None:
            raise serializers.ValidationError("Invalid username.")
        return value

    def create(self, validated_data):
        force_byte = utils.encoding.force_bytes(self.user.pk)
        uid = utils.http.urlsafe_base64_encode(force_byte)
        token = auth.tokens.default_token_generator.make_token(self.user)

        tasks.email_forget_password.delay(uid, token, self.user.email)
        return dict()


class ResetPasswordSerializer(serializers.Serializer):
    uid = serializers.CharField(write_only=True)
    token = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate_uid(self, value):
        pk = utils.http.urlsafe_base64_decode(value).decode()
        self.user = models.User.objects.filter(pk=pk).first()
        if self.user is None:
            raise serializers.ValidationError("Invalid uid.")
        return value

    def validate_password(self, value):
        try:
            auth.password_validation.validate_password(value)
            self.encrypted_password = auth.hashers.make_password(value)
            return value
        except exceptions.ValidationError as error:
            raise serializers.ValidationError(
                "Use 8 or more characters with a mix of letters, numbers & symbols"
            )

    def validate(self, data):
        if (
            auth.tokens.default_token_generator.check_token(self.user, data["token"])
            is False
        ):
            raise serializers.ValidationError(dict(token="Invalid token."))

        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                dict(confirm_password="Password mismatch.")
            )
        return data

    @transaction.atomic
    def create(self, validated_data):
        self.user.password = self.encrypted_password
        self.user.transaction_password = self.encrypted_password
        self.user.save(update_fields=["password", "transaction_password"])
        return dict()
