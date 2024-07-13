from rest_framework import serializers

from invest import models


class AdminInvestSerializer(serializers.ModelSerializer):
    contract_code = serializers.CharField(source="contract.code", read_only=True)
    contract_title = serializers.CharField(source="contract.title", read_only=True)
    stake_user_id = serializers.IntegerField(source="stake.user.id", read_only=True)
    stake_user_username = serializers.CharField(
        source="stake.user.username", read_only=True
    )

    class Meta:
        model = models.Invest
        fields = "__all__"


class AdminInvestBonusTransactionSerializer(serializers.ModelSerializer):
    invest_contract_code = serializers.CharField(
        source="invest.contract.code", read_only=True
    )
    invest_contract_title = serializers.CharField(
        source="invest.contract.title", read_only=True
    )
    invest_stake_user_id = serializers.IntegerField(
        source="invest.stake.user.id", read_only=True
    )
    invest_stake_user_username = serializers.CharField(
        source="invest.stake.user.username", read_only=True
    )

    class Meta:
        model = models.InvestBonusTransaction
        fields = "__all__"
