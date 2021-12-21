import datetime
import json
import pandas as pd
import requests

from typing import Any

def help():
    return "This was loaded ok"

def get_data() -> Any:

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

    data = '{"operationName":"ContractInteractionsQuery","variables":{"id":"A.8b148183c28ff88f.Gaia","limit":25,"offset":0},"query":"query ContractInteractionsQuery($id: ID!, $limit: Int!, $offset: Int) {\\n  contract(id: $id) {\\n    interactions(limit: $limit, offset: $offset) {\\n      count\\n      edges {\\n        node {\\n          time\\n          id\\n          proposer {\\n            address\\n            __typename\\n          }\\n          status\\n          eventTypes(contractIds: [$id]) {\\n            fullId\\n            __typename\\n          }\\n          __typename\\n        }\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n"}'  # noqa

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

    evt_zero = tx_events[0]["node"]
    expected_type = "A.ead892083b3e2c6c.DapperUtilityCoin.TokensWithdrawn"

    if evt_zero["indexInTransaction"] != 0 or evt_zero["eventType"]["fullId"] != expected_type:
        return None

    evt_one = tx_events[1]["node"]

    return {
        "private_token_id": int(evt_one["fields"][0]["value"]),
        "price": float(evt_zero["fields"][0]["value"]),
        "time": str(datetime.datetime.fromtimestamp(float(time))),
        "seller": evt_one["fields"][1]["value"]["value"],
        "transaction": id,
    }

def matches_top_level_events(x: Any) -> bool:
    types = str(x["node"]["eventTypes"])
    result = "A.8b148183c28ff88f.Gaia.Deposit" in types and "A.8b148183c28ff88f.Gaia.Withdraw" in types
    return result

def make_wallet_clickable(x: str) -> str:
    link = f"https://ballerz.info/?wallet={x}"
    return f'<a target="_blank" href="{link}">{x}</a>'

def make_tx_clickable(x: str) -> str:
    link = f"https://flowscan.org/transaction/{x}"
    return f'<a target="_blank" href="{link}">{x}</a>'

def get_sales_df() -> pd.DataFrame:

    response = get_data()
    edges = response["data"]["contract"]["interactions"]["edges"]
    transactions = [transaction_info(x["node"]["time"], x["node"]["id"]) for x in edges if matches_top_level_events(x)]  # noqa
    transactions = [tx for tx in transactions if tx is not None]

    df = pd.DataFrame(transactions)
    # link is the column with hyperlinks
    df['transaction'] = df['transaction'].apply(make_tx_clickable)
    df['seller'] = df['seller'].apply(make_wallet_clickable)
    df = df.to_html(escape=False)
    return df


    
