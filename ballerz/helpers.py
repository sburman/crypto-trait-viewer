import arrow
import datetime
import json
import pandas as pd
import requests

from typing import Any

def load_id_mappings() -> pd.DataFrame:
    path = "./ballerz/ballerz_id_mapping.csv"
    df = pd.read_csv(path)
    df = df[df["transaction_token_id"] != 0]
    return df

ID_MAPS = load_id_mappings()

print("LOADED ID MAPS:", len(ID_MAPS))
print(ID_MAPS.columns)    

def get_page_data(page: int = 1) -> Any:

    offset = (page - 1) * 25
    print("get_page_data", "offset", offset)
    headers = {
        'authority': 'flowscan.org',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
        'accept': '*/*',
        'content-type': 'application/json',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',  # noqa
        'sec-ch-ua-platform': '"Linux"',
        'origin': 'https://flowscan.org',
    }

    data = '{"operationName":"ContractInteractionsQuery","variables":{"id":"A.8b148183c28ff88f.Gaia","limit":25,"offset":' + str(offset) + '},"query":"query ContractInteractionsQuery($id: ID!, $limit: Int!, $offset: Int) {\\n  contract(id: $id) {\\n    interactions(limit: $limit, offset: $offset) {\\n      count\\n      edges {\\n        node {\\n          time\\n          id\\n          proposer {\\n            address\\n            __typename\\n          }\\n          status\\n          eventTypes(contractIds: [$id]) {\\n            fullId\\n            __typename\\n          }\\n          __typename\\n        }\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n"}'  # noqa

    response = requests.post('https://flowscan.org/query', headers=headers, data=data)

    return json.loads(response.text)

def get_detail(id: str) -> Any:
    headers = {
        'authority': 'flowscan.org',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
        'accept': '*/*',
        'content-type': 'application/json',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
        'sec-ch-ua-platform': '"Linux"',
        'origin': 'https://flowscan.org',
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
    baller_id_result = ID_MAPS[ID_MAPS["transaction_token_id"] == transaction_token_id]
    if len(baller_id_result) != 1:
        print("Could not map transaction id:", transaction_token_id)
        return None
    baller_id = baller_id_result.iloc[0]["public_token_id"]

    return {
        "baller_id": baller_id,
        "price": price,
        "time": arrow.get(float(time)).humanize(),
        "buyer": buyer,
        "seller": seller,
        "transaction": id,
        "transaction_token_id": transaction_token_id,
    }

def matches_top_level_events(x: Any) -> bool:
    types = str(x["node"]["eventTypes"])
    result = "A.8b148183c28ff88f.Gaia.Deposit" in types and "A.8b148183c28ff88f.Gaia.Withdraw" in types
    return result

def make_wallet_clickable(x: str) -> str:
    link = f"https://ballerz.info/?wallet={x}"
    return f'<a target="_blank" href="{link}">{x}</a>'

def make_baller_id_clickable(x: str) -> str:
    link = f"https://ballerz.info/?ballerz-id={x}"
    return f'<a target="_blank" href="{link}">{x}</a>'

def make_tx_clickable(x: str) -> str:
    link = f"https://flowscan.org/transaction/{x}"
    return f'<a target="_blank" href="{link}">{x}</a>'

def get_sales_df_for_page(page: int = 1) -> pd.DataFrame:

    response = get_page_data(page)
    edges = response["data"]["contract"]["interactions"]["edges"]
    transactions = [transaction_info(x["node"]["time"], x["node"]["id"]) for x in edges if matches_top_level_events(x)]  # noqa
    transactions = [tx for tx in transactions if tx is not None]

    df = pd.DataFrame(transactions)
    # link is the column with hyperlinks
    df['baller_id'] = df['baller_id'].apply(make_baller_id_clickable)
    df['price'] = df['price'].apply(lambda x: f"${x:.0f}")
    df['transaction'] = df['transaction'].apply(make_tx_clickable)
    df['buyer'] = df['buyer'].apply(make_wallet_clickable)
    df['seller'] = df['seller'].apply(make_wallet_clickable)
    df = df.to_html(escape=False)
    return df


    
