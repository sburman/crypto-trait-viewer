import streamlit as st

import arrow
import datetime
import json
import pandas as pd
import requests

from typing import Any

from .helpers import *

def get_listings_page(page: int = 1) -> Any:

    offset = (page - 1) * 25
    headers = {
        'content-type': 'application/json',
    }

    data = '{"operationName":"ContractInteractionsQuery","variables":{"id":"A.4eb8a10cb9f87357.NFTStorefront","limit":25,"offset":' + str(offset) + '},"query":"query ContractInteractionsQuery($id: ID!, $limit: Int!, $offset: Int) {\\n  contract(id: $id) {\\n    interactions(limit: $limit, offset: $offset) {\\n      count\\n      edges {\\n        node {\\n          time\\n          id\\n          proposer {\\n            address\\n            __typename\\n          }\\n          status\\n          eventTypes(contractIds: [$id]) {\\n            fullId\\n            __typename\\n          }\\n          __typename\\n        }\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n"}'

    response = requests.post('https://flowscan.org/query', headers=headers, data=data)

    return json.loads(response.text)

def get_listing_detail(id: str) -> Any:
    headers = {
        'content-type': 'application/json',
    }
    data = '{"operationName":"TransactionEventsSectionQuery","variables":{"id":"' + id + '","limit":20,"offset":0},"query":"query TransactionEventsSectionQuery($id: ID!, $eventTypeFilter: [ID!], $limit: Int, $offset: Int) {\\n  checkTransaction(id: $id) {\\n    transaction {\\n      eventTypes {\\n        fullId\\n        __typename\\n      }\\n      events(first: $limit, skip: $offset, type: $eventTypeFilter) {\\n        edges {\\n          node {\\n            indexInTransaction\\n            eventType {\\n              fullId\\n              __typename\\n            }\\n            fields\\n            __typename\\n          }\\n          __typename\\n        }\\n        count\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n"}'

    response = requests.post('https://flowscan.org/query', headers=headers, data=data)

    return json.loads(response.text)

def listing_info(time: str, id: str) -> Any:

    response = get_listing_detail(id)
    tx_events = response["data"]["checkTransaction"]["transaction"]["events"]["edges"]

    if len(tx_events) != 4:
        return None

    evt_listing = tx_events[0]["node"]
    evt_listing_type = "A.4eb8a10cb9f87357.NFTStorefront.ListingAvailable"
    if evt_listing["indexInTransaction"] != 0 or evt_listing["eventType"]["fullId"] != evt_listing_type:
        return None

        # storefrontAddress: Address,
        # listingResourceID: UInt64,
        # nftType: Type,
        # nftID: UInt64,
        # ftVaultType: Type,
        # price: UFix64

    token_type = evt_listing["fields"][2]["value"]["staticType"]
    if token_type != "A.8b148183c28ff88f.Gaia.NFT":
        return None

    seller = evt_listing["fields"][0]["value"]
    transaction_token_id = int(evt_listing["fields"][3]["value"])
    price = float(evt_listing["fields"][5]["value"])

    # map baller id from transaction token
    baller_result = BALLERZ[BALLERZ["transaction_token_id"] == transaction_token_id]
    if len(baller_result) != 1:
        return None
    baller = baller_result.iloc[0]

    return {
        "baller_id": baller["baller_id"],
        "image": baller["Image"],
        "price": price,
        "combo": baller["Combo Rank"],
        "rarity": baller["Trait Rank"],
        "skill": baller["Skill Rank"],
        "team": baller["Team"],
        "role": baller["Role"],
        "time": arrow.get(float(time)).humanize(),
        "seller": seller,
        "transaction_id": id,
    }

def matches_top_level_events(x: Any) -> bool:
    types = str(x["node"]["eventTypes"])
    result = "A.4eb8a10cb9f87357.NFTStorefront.ListingAvailable" in types
    return result

def get_raw_df_for_page(page: int = 1) -> pd.DataFrame:
    response = get_listings_page(page)
    edges = response["data"]["contract"]["interactions"]["edges"]
    transactions = [listing_info(x["node"]["time"], x["node"]["id"]) for x in edges if matches_top_level_events(x)]  # noqa
    transactions = [tx for tx in transactions if tx is not None]

    return pd.DataFrame(transactions)

def direct_listing_link(x: str) -> str:
    link = f"https://ongaia.com/ballerz/{x}"
    return f'<a target="_blank" href="{link}">{x}</a>'

def get_display_df_for_page(page: int = 1) -> pd.DataFrame:

    df = get_raw_df_for_page(page)
    
    # make it prettier for ux
    df['info'] = df['baller_id'].apply(make_baller_id_clickable)
    df['baller_id'] = df['baller_id'].apply(direct_listing_link)
    df['price'] = df['price'].apply(lambda x: f"${x:.0f}")
    df['transaction_id'] = df['transaction_id'].apply(make_tx_clickable)
    df['seller'] = df['seller'].apply(make_wallet_clickable)
    df['image'] = df['image'].apply(path_to_image_html)
    df = df.to_html(escape=False)
    return df

def display() -> Any:
    st.title("Ballerz Recent Listingz")

    page_choice = st.sidebar.selectbox('Page?', [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    df = get_display_df_for_page(page_choice)
    st.write(df, unsafe_allow_html=True)

    
