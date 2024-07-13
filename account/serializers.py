from rest_framework import serializers

from account import models


class AccountSerializer(serializers.ModelSerializer):
    account_type_display = serializers.ChoiceField(
        source="get_account_type_display",
        choices=[i[1] for i in models.Account.ACCOUNT_TYPES],
    )

    class Meta:
        model = models.Account
        exclude = ["user"]
