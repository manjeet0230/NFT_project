 # nftapp/views.py
from django.shortcuts import render
from django.http import HttpResponseRedirect
from xrpl.models.requests import NFTSellOffers, NFTBuyOffers, NFTSellOffers
from nft_api.forms import *
from xrpl.wallet import Wallet
from xrpl.transaction import submit_and_wait
from xrpl.models.transactions.nftoken_mint import NFTokenMint, NFTokenMintFlag
from xrpl.wallet import generate_faucet_wallet
from xrpl.models.transactions import NFTokenAcceptOffer, NFTokenCancelOffer
from xrpl.clients import JsonRpcClient
from xrpl import transaction
import base58
import ipfsApi
import json
import xrpl
from xrpl.models.requests import AccountNFTs
from datetime import datetime
from datetime import timedelta
from django.http import JsonResponse



def create_nft(request):
    if request.method == 'POST':
        form = NFTForm(request.POST, request.FILES)
        if form.is_valid():
            # Process form data
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            author = form.cleaned_data['author']
            image = form.cleaned_data['image']

            # Connect to IPFS and add image
            api = ipfsApi.Client('127.0.0.1', 5001)
            metadata = {
                "title": title,
                "description": description,
                "author": author,
            }
            res = api.add(image, json=json.dumps(metadata))
            # print(res)
            ipfs_cid = res.get('Hash')
            hex_value = ipfs_cid.encode('utf-8').hex()

            # Connect to XRPL testnet node
            JSON_RPC_URL = "https://s.altnet.rippletest.net:51234/"
            client = JsonRpcClient(JSON_RPC_URL)

            # Load issuer wallet
            seed = "sEdVCTF3VipJSa4U6s1sfCiuokBDpgf"  # Replace with your seed
            issuer_wallet = Wallet.from_seed(seed=seed)
            issuerAddr = issuer_wallet.address

            # Construct NFTokenMint transaction
            mint_tx = NFTokenMint(
                account=issuerAddr,
                nftoken_taxon=1,
                flags=NFTokenMintFlag.TF_TRANSFERABLE,
                uri=hex_value,
            )

            # Sign and submit transaction
            # Sign and submit transaction
            mint_tx_response = submit_and_wait(transaction=mint_tx, client=client, wallet=issuer_wallet)
            mint_tx_result = mint_tx_response.result
            print(mint_tx_result)

            # Handle transaction result and metadata
            nft_metadata_list = []
            for node in mint_tx_result['meta']['AffectedNodes']:
                if "CreatedNode" in node:
                    nft_metadata_list.append(node['CreatedNode']['NewFields']['NFTokens'][0]['NFToken'])

            # Make sure the return statement is outside the for loop
            return render(request, 'nft_api/mint_success.html', {'nft_metadata_list': nft_metadata_list})


    else:
        form = NFTForm()

    return render(request, 'nft_api/mint_form.html', {'form': form})






def create_sell_offer_view(request):
    testnet_url = "https://s.altnet.rippletest.net:51234/"  # Define your testnet URL
    if request.method == 'POST':
        form = SellOfferForm(request.POST)
        if form.is_valid():
            seed = form.cleaned_data['seed']
            amount = form.cleaned_data['amount']
            nftoken_id = form.cleaned_data['nftoken_id']
            expiration = form.cleaned_data['expiration']

            owner_wallet = Wallet.from_seed(seed=seed, algorithm="ed25519")
            client = JsonRpcClient(testnet_url)
            expiration_date = datetime.now()

            if expiration:
                expiration_timedelta = timedelta(seconds=int(expiration))
                expiration_date = datetime.now() + expiration_timedelta
                expiration_date = xrpl.utils.datetime_to_ripple_time(expiration_date)

            sell_offer_tx = xrpl.models.transactions.NFTokenCreateOffer(
                account=owner_wallet.classic_address,
                nftoken_id=nftoken_id,
                amount=str(amount),
                expiration=expiration_date if expiration else None,
                flags=1
            )

            print(sell_offer_tx)

            response = submit_and_wait(sell_offer_tx, client, owner_wallet)

            # Assuming successful response (update with actual response check)
            if response:
                return render(request, 'nft_api/success_sell.html')
    else:
        form = SellOfferForm()

    return render(request, 'nft_api/create_sell_offer.html', {'form': form})


def accept_sell_offer_view(request):
    testnet_url = "https://s.altnet.rippletest.net:51234/"  # Define your testnet URL

    if request.method == 'POST':
        offer_index = request.POST.get('offer_index')  # Assuming you send the offer_index as a POST parameter
        
        seed = "sEd7Y3ubWnxcdmycr1yokAm7XzmsDDe"
        buyer_wallet = Wallet.from_seed(seed=seed, algorithm="ed25519")
        client = JsonRpcClient(testnet_url)

        accept_offer_tx = xrpl.models.transactions.NFTokenAcceptOffer(
            account=buyer_wallet.classic_address,
            nftoken_sell_offer=offer_index
        )
        
        response = submit_and_wait(accept_offer_tx, client, buyer_wallet)
            
        return render(request, 'nft_api/success_accept_sell_offer.html', {'response': response})

    return render(request, 'nft_api/accept_sell_offer.html')


def create_buy_offer_view(request):
    testnet_url = "https://s.altnet.rippletest.net:51234/"  # Define your testnet URL

    if request.method == 'POST':
        form = BuyOfferForm(request.POST)
        if form.is_valid():
            seed = form.cleaned_data['seed']
            amount = form.cleaned_data['amount']
            nft_id = form.cleaned_data['nft_id']
            owner = form.cleaned_data['owner']
            expiration = form.cleaned_data['expiration']

            # Get the client
            buyer_wallet = Wallet.from_seed(seed=seed, algorithm="ed25519")
            client = JsonRpcClient(testnet_url)
            expiration_date = datetime.now()
            if expiration:
                expiration_timedelta = timedelta(seconds=int(expiration))
                expiration_date = datetime.now() + expiration_timedelta
                expiration_date = xrpl.utils.datetime_to_ripple_time(expiration_date)
            
            # Define the buy offer transaction with an expiration date
            buy_offer_tx = xrpl.models.transactions.NFTokenCreateOffer(
                account=buyer_wallet.classic_address,
                nftoken_id=nft_id,
                amount=str(amount),
                owner=owner,
                expiration=expiration_date if expiration else None,
                flags=0
            )
            
            # Sign and fill the transaction
            response = submit_and_wait(buy_offer_tx, client, buyer_wallet)
            
            return render(request, 'nft_api/buy_offer_success.html', {'response': response})
    else:
        form = BuyOfferForm()

    return render(request, 'nft_api/create_buy_offer.html', {'form': form})


# def accept_buy_offer_view(request, offer_index):
#     """accept_buy_offer_view"""
#     form = AcceptBuyOfferForm(request.POST or None)
#     if request.method == 'POST' and form.is_valid():
#         seed = form.cleaned_data['seed']

#         buyer_wallet = Wallet.from_seed(seed=seed, algorithm="ed25519")
#         client = JsonRpcClient(testnet_url)

#         accept_offer_tx = NFTokenAcceptOffer(
#             account=buyer_wallet.classic_address,
#             nftoken_buy_offer=offer_index
#         )

#         response = submit_and_wait(accept_offer_tx, client, buyer_wallet)

#         return render(request, 'nft_api/accept_buy_offer_success.html', {'response': response})

#     return render(request, 'nft_api/accept_buy_offer.html', {'offer_index': offer_index, 'accept_buy_offer_form': form})

# def get_offers_view(request, nft_id):
#     """get_offers_view"""
#     client = JsonRpcClient(testnet_url)

#     offers_request = NFTBuyOffers(nft_id=nft_id)
#     response = client.request(offers_request)
#     buy_offers = json.dumps(response.result, indent=4)

#     sell_offers_request = NFTSellOffers(nft_id=nft_id)
#     response = client.request(sell_offers_request)
#     sell_offers = json.dumps(response.result, indent=4)

#     all_offers = f"Buy Offers:\n{buy_offers}\n\nSell Offers:\n{sell_offers}"
#     return render(request, 'nft_api/offers.html', {'offers': all_offers})

# def cancel_offer_view(request, nftoken_offer_ids):
#     """cancel_offer_view"""
#     form = CancelOfferForm(request.POST or None)
#     if request.method == 'POST' and form.is_valid():
#         seed = form.cleaned_data['seed']

#         owner_wallet = Wallet.from_seed(seed=seed, algorithm="ed25519")
#         client = JsonRpcClient(testnet_url)

#         token_offer_ids = [nftoken_offer_ids]

#         cancel_offer_tx = NFTokenCancelOffer(
#             account=owner_wallet.classic_address,
#             nftoken_offers=token_offer_ids
#         )

#         response = submit_and_wait(cancel_offer_tx, client, owner_wallet)

#         return render(request, 'nft_api/cancel_offer_success.html', {'response': response})

#     return render(request, 'nft_api/cancel_offer.html', {'nftoken_offer_ids': nftoken_offer_ids, 'cancel_offer_form': form})








# # nft_app/views.py
# from django.shortcuts import render
# from xrpl.transaction import submit_and_wait
# from xrpl.models.transactions.nftoken_mint import NFTokenMint, NFTokenMintFlag
# from xrpl.wallet import Wallet
# from xrpl.clients import JsonRpcClient
# import base58
# import ipfsApi
# import json
# from .forms import NFTForm





