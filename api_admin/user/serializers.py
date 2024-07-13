from django.db import transaction

from rest_framework import serializers

from user import serializers as user_serializers, models as user_models


class AdminUserSerializer(serializers.ModelSerializer):
    attachments = user_serializers.UserAttachmentSerializer(many=True, read_only=True)
    status = serializers.ChoiceField(
        choices=[i[0] for i in user_models.User.USER_STATUS]
    )
    username = serializers.CharField(read_only=True)
    details = user_serializers.UserDetailsSerializer()
    contact = user_serializers.UserContactSerializer()
    attachments = user_serializers.UserAttachmentSerializer(many=True, read_only=True)
    status_display = serializers.ChoiceField(
        source="get_status_display",
        read_only=True,
        choices=[i[1] for i in user_models.User.USER_STATUS],
    )

    class Meta:
        model = user_models.User
        fields = "__all__"

    def validate(self, attrs):
        status = attrs.get("status", None)
        if (
            not status is None
            and status == user_models.User.REJECTED
            and not attrs.get("remark", "")
        ):
            raise serializers.ValidationError({"remark": "Remark is required"})
        return super().validate(attrs)

    @transaction.atomic
    def update(self, instance, validated_data):
        details = validated_data.pop("details", None)
        if not details is None:
            sub_instance = (
                instance.details
                if hasattr(instance, "details")
                else user_models.UserDetails(user=instance)
            )
            serialized = user_serializers.UserDetailsSerializer(
                instance=sub_instance, data=details
            )
            serialized.is_valid(raise_exception=True)
            serialized.save()

        contact = validated_data.pop("contact", None)
        if not contact is None:
            sub_instance = (
                instance.contact
                if hasattr(instance, "contact")
                else user_models.UserContact(user=instance)
            )
            serialized = user_serializers.UserContactSerializer(
                instance=sub_instance, data=contact
            )
            serialized.is_valid(raise_exception=True)
            serialized.save()

        return super().update(instance, validated_data)
