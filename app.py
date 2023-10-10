import os
import json
import logging
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

logging.basicConfig(level = logging.INFO)

def load_env():
    if load_dotenv():
        logging.info('dotenv loaded')
        st.sidebar.text('dotenv loaded')
    else:
        logging.info('dotenv loading failed')
        st.sidebar.text('dotenv loading failed')

def connect_w3():
   w3_instance =  Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))
   if w3_instance.isConnected():
       logging.info('Connected to Web3 Provider')
       st.sidebar.text('Connected to Web3 Provider')

   else:
       logging.info('Connected to Web3 Provider failed')
       st.sidebar.text('Connected to Web3 Provider failed')
   return w3_instance

@st.cache_resource()
def load_contract():
    with open(Path('./contracts/compiled/artwork_abi.json')) as f:
        artwork_abi = json.load(f)

    contract_address = os.getenv("SMART_CONTRACT_ADDRESS")
    return w3.eth.contract(address=contract_address, abi=artwork_abi)    


def register_artwork():
    address = st.selectbox("Select Artwork Owner", options=accounts)
    artwork_uri = st.text_input("The URI to the artwork")

    if st.button("Register Artwork"):
        tx_hash = contract.functions.registerArtwork(address, artwork_uri).transact({'from': address, 'gas': 1000000})
        receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        if receipt.status:
            st.success(f"Artwork Registered! Transaction Hash: {tx_hash.hex()}")
            logging.info(f"Artwork registered with Transaction Hash: {tx_hash.hex()}")
            st.sidebar.text(f"Artwork registered with Transaction Hash: {tx_hash.hex()}")
        else:
            st.error("Transaction Failed!")
            logging.error("Transaction Failed!")

def query_nft_by_address():
    st.subheader("Query NFTs by Address")
    query_address = st.text_input("Enter Ethereum address to fetch associated NFTs")

    if st.button("Fetch NFTs"):
        token_count = contract.functions.balanceOf(query_address).call()
        nft_tokens = [contract.functions.tokenOfOwnerByIndex(query_address, i).call() for i in range(token_count)]
        for token in nft_tokens:
            token_uri = contract.functions.tokenURI(token).call()
            st.write(f"Token ID: {token} - Artwork: {token_uri}")

# Display a token's details
def display_token_details():
    st.markdown("## Check Ownership and Display Token")
    token_id = st.selectbox("Artwork Tokens", list(range(contract.functions.totalSupply().call())))
    if st.button("Display Token Details"):
        owner = contract.functions.ownerOf(token_id).call()
        st.write(f"Owner: {owner}")
        token_uri = contract.functions.tokenURI(token_id).call()
        st.write(f"Token URI: {token_uri}")
        st.image(token_uri)

def main():
    st.title("NFT Artwork Registry")
    register_artwork()
    st.markdown("---")
    query_nft_by_address()
    st.markdown("---")
    display_token_details()

if __name__ == "__main__":
    st.sidebar.title("Logs and Status")
    load_env()
    w3 = connect_w3()
    accounts = w3.eth.accounts
    contract = load_contract()
    main()