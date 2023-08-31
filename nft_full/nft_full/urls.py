# nftapp/urls.py
from django.urls import path
from nft_api import views
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('mint/', views.create_nft, name='mint_nft'),
    path('sell/', views.create_sell_offer_view, name='create_sell_offer'),
    path('accept_sell_offer/', views.accept_sell_offer_view, name='accept_sell_offer'),
    path('create_buy_offer/', views.create_buy_offer_view, name='create_buy_offer'),
#     path('accept_buy_offer/<int:offer_index>/', views.accept_buy_offer_view, name='accept_buy_offer'),
#     path('get_offers/<str:nft_id>/', views.get_offers_view, name='get_offers'),
#     path('cancel_offer/<int:nftoken_offer_ids>/', views.cancel_offer_view, name='cancel_offer'),
]
