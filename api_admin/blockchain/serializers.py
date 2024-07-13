from rest_framework import serializers

from upload import serializers as upload_serializers

from blockchain import models


class AdminBlockchainWalletSerializer(serializers.ModelSerializer):
    attachment = upload_serializers.UploadSerializer(read_only=True)

    class Meta:
        model = models.BlockchainWallet
        fields = "__all__"
