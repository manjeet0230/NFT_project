from rest_framework import serializers
from .models import NFT

class NFTSerializer(serializers.ModelSerializer):
    class Meta:
        model = NFT
        fields = ('id', 'title', 'description', 'author', 'image')
