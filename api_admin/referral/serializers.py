from rest_framework import serializers

from referral import models


class AdminReferralSerializer(serializers.ModelSerializer):
    referrer_username = serializers.CharField(
        source="referrer.username", read_only=True
    )
    referred_username = serializers.CharField(
        source="referred.username", read_only=True
    )
    referred_first_name = serializers.CharField(
        source="referred.first_name", read_only=True
    )
    referred_last_name = serializers.CharField(
        source="referred.last_name", read_only=True
    )

    class Meta:
        model = models.Referral
        fields = "__all__"


class AdminReferralBonusSettingsSerializer(serializers.ModelSerializer):
    term_title = serializers.CharField(source="term.title", read_only=True)
    term_days = serializers.CharField(source="term.days", read_only=True)

    class Meta:
        model = models.ReferralBonusSettings
        fields = "__all__"


class AdminReferralBonusTransactionSerializer(serializers.ModelSerializer):
    referrer_username = serializers.CharField(
        source="referrer.username", read_only=True
    )
    user_username = serializers.CharField(source="user.username", read_only=True)
    term_title = serializers.CharField(source="term.title", read_only=True)

    class Meta:
        model = models.ReferralBonusTransaction
        fields = "__all__"
