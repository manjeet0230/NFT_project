from django.contrib import admin
from .models import NFT

@admin.register(NFT)
class NFTAdmin(admin.ModelAdmin):
    list_display = ('title', 'description','author', 'image')
    search_fields = ('title', 'description','author', 'image')