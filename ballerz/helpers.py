import pandas as pd

HISTORY_FILE = './ballerz/ballerz_sales_history.csv'
HISTORY_LISTINGS_FILE = './ballerz/ballerz_listing_history.csv'

def load_id_mappings() -> pd.DataFrame:
    path = "./ballerz/ballerz_id_mapping.csv"
    df = pd.read_csv(path)
    df = df[df["transaction_token_id"] != 0]
    return df

def load_ballerz_info() -> pd.DataFrame:
    id_maps = load_id_mappings()
    path = "./ballerz/BallerzStreamlit_v7.csv"
    df = pd.read_csv(path)
    df = df.merge(id_maps, left_on='baller_id', right_on='public_token_id')
    return df

BALLERZ = load_ballerz_info()
print("LOADED BALLERZ:", BALLERZ.shape)

def make_wallet_clickable(x: str) -> str:
    link = f"https://ballerz.info/?wallet={x}"
    return f'<a target="_blank" href="{link}">{x}</a>'

def make_baller_id_clickable(x: str) -> str:
    link = f"https://ballerz.info/?ballerz-id={x}"
    return f'<a target="_blank" href="{link}">#{x}</a>'

def make_tx_clickable(x: str) -> str:
    link = f"https://flowscan.org/transaction/{x}"
    return f'<a target="_blank" href="{link}">...{x[-7:]}</a>'

def path_to_image_html(path):
    return '<img src="'+ path + '" style=max-height:64px;"/>'
