import streamlit as st

import arrow
import datetime
import json
import pandas as pd
import requests

from typing import Any

from .helpers import *

def get_page_data(page: int = 1) -> Any:

    offset = (page - 1) * 25
    headers = {
        'content-type': 'application/json',
    }

    data = '{"operationName":"ContractInteractionsQuery","variables":{"id":"A.8b148183c28ff88f.Gaia","limit":25,"offset":' + str(offset) + '},"query":"query ContractInteractionsQuery($id: ID!, $limit: Int!, $offset: Int) {\\n  contract(id: $id) {\\n    interactions(limit: $limit, offset: $offset) {\\n      count\\n      edges {\\n        node {\\n          time\\n          id\\n          proposer {\\n            address\\n            __typename\\n          }\\n          status\\n          eventTypes(contractIds: [$id]) {\\n            fullId\\n            __typename\\n          }\\n          __typename\\n        }\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n"}'  # noqa

    response = requests.post('https://flowscan.org/query', headers=headers, data=data)

    return json.loads(response.text)

def get_detail(id: str) -> Any:
    headers = {
        'content-type': 'application/json',
    }

    data = '{"operationName":"TransactionEventsSectionQuery","variables":{"id":"' + id + '","limit":20,"offset":0},"query":"query TransactionEventsSectionQuery($id: ID!, $eventTypeFilter: [ID!], $limit: Int, $offset: Int) {\\n  checkTransaction(id: $id) {\\n    transaction {\\n      eventTypes {\\n        fullId\\n        __typename\\n      }\\n      events(first: $limit, skip: $offset, type: $eventTypeFilter) {\\n        edges {\\n          node {\\n            indexInTransaction\\n            eventType {\\n              fullId\\n              __typename\\n            }\\n            fields\\n            __typename\\n          }\\n          __typename\\n        }\\n        count\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n"}'

    response = requests.post('https://flowscan.org/query', headers=headers, data=data)

    return json.loads(response.text)

def transaction_info(time: str, id: str) -> Any:

    response = get_detail(id)
    tx_events = response["data"]["checkTransaction"]["transaction"]["events"]["edges"]

    if len(tx_events) != 18:
        return None

    evt_price = tx_events[0]["node"]
    evt_price_type = "A.ead892083b3e2c6c.DapperUtilityCoin.TokensWithdrawn"
    if evt_price["indexInTransaction"] != 0 or evt_price["eventType"]["fullId"] != evt_price_type:
        return None
    price = float(evt_price["fields"][0]["value"])

    evt_seller = tx_events[1]["node"]
    evt_seller_type = "A.8b148183c28ff88f.Gaia.Withdraw"
    if evt_seller["indexInTransaction"] != 1 or evt_seller["eventType"]["fullId"] != evt_seller_type:
        return None
    seller = evt_seller["fields"][1]["value"]["value"]

    evt_buyer = tx_events[14]["node"]
    evt_buyer_type = "A.8b148183c28ff88f.Gaia.Deposit"
    if evt_buyer["indexInTransaction"] != 14 or evt_buyer["eventType"]["fullId"] != evt_buyer_type:
        return None
    buyer = evt_buyer["fields"][1]["value"]["value"]
    transaction_token_id = int(evt_buyer["fields"][0]["value"])
    buyer = evt_buyer["fields"][1]["value"]["value"]

    # map baller id from transaction token
    baller_result = BALLERZ[BALLERZ["transaction_token_id"] == transaction_token_id]
    if len(baller_result) != 1:
        print("Could not map transaction id:", transaction_token_id)
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
        "buyer": buyer,
        "seller": seller,
        "transaction_id": id,
    }

def matches_top_level_events(x: Any) -> bool:
    types = str(x["node"]["eventTypes"])
    result = "A.8b148183c28ff88f.Gaia.Deposit" in types and "A.8b148183c28ff88f.Gaia.Withdraw" in types
    return result

def get_raw_df_for_page(page: int = 1) -> pd.DataFrame:
    response = get_page_data(page)
    edges = response["data"]["contract"]["interactions"]["edges"]
    transactions = [transaction_info(x["node"]["time"], x["node"]["id"]) for x in edges if matches_top_level_events(x)]  # noqa
    transactions = [tx for tx in transactions if tx is not None]

    return pd.DataFrame(transactions)

def get_display_df_for_page(page: int = 1) -> pd.DataFrame:

    df = get_raw_df_for_page(page)
    
    # make it prettier for ux
    df['baller_id'] = df['baller_id'].apply(make_baller_id_clickable)
    df['price'] = df['price'].apply(lambda x: f"${x:.0f}")
    df['transaction_id'] = df['transaction_id'].apply(make_tx_clickable)
    df['buyer'] = df['buyer'].apply(make_wallet_clickable)
    df['seller'] = df['seller'].apply(make_wallet_clickable)
    df['image'] = df['image'].apply(path_to_image_html)
    df = df.to_html(escape=False)
    return df

def display() -> Any:
    st.title("Ballerz Recent Salez")

    page_choice = st.sidebar.selectbox('Page?', [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    df = get_display_df_for_page(page_choice)
    st.write(df, unsafe_allow_html=True)


    
