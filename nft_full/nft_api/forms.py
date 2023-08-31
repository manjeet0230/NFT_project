# nftapp/forms.py
from django import forms

class NFTForm(forms.Form):
    title = forms.CharField(max_length=100)
    description = forms.CharField(widget=forms.Textarea)
    author = forms.CharField(max_length=50)
    image = forms.ImageField()


class SellOfferForm(forms.Form):
    seed = forms.CharField(max_length=128)
    amount = forms.DecimalField()
    nftoken_id = forms.CharField(max_length=64)
    expiration = forms.IntegerField(required=False)


class AcceptSellOfferForm(forms.Form):
    offer_index = forms.CharField(label='Offer Index', max_length=100)

class BuyOfferForm(forms.Form):
    seed = forms.CharField(max_length=64)
    amount = forms.DecimalField()
    nft_id = forms.CharField(max_length=64)
    owner = forms.CharField(max_length=50)
    expiration = forms.IntegerField(required=False)

class AcceptBuyOfferForm(forms.Form):
    seed = forms.CharField(max_length=64, widget=forms.PasswordInput)

class CancelOfferForm(forms.Form):
    seed = forms.CharField(max_length=64, widget=forms.PasswordInput)
