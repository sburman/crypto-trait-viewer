#!/usr/bin/env python

import datetime
from datetime import datetime, timedelta
    
import pandas as pd

from .sales import *
from .helpers import HISTORY_FILE

def update_sales() -> pd.DataFrame:

    df = pd.read_csv(HISTORY_FILE, index_col='datetime')
    
    # # restores datetime index from timestamp
    # df = pd.read_csv(HISTORY_FILE)
    # df["datetime"] = df['timestamp'].apply(lambda x: arrow.get(int(x)).datetime)
    # df.set_index('datetime', inplace=True)

    latest_updated = df.index.max()
    print("Existing from", df.index.min(), "to", latest_updated)
    
    max_pages = 200
    page_updates = []
    for i in range(1, max_pages + 1):
        
        page = get_raw_df_for_page(i)
        print(f"Page {i} from", page.index.min(), "to", page.index.max())
        page_newer_filtered = page[page.index > latest_updated]
        page_updates.append(page_newer_filtered)

        # if we dropped any entries we know we have overlapped the time
        if page.shape[0] != page_newer_filtered.shape[0]:
            print("!!! Stopping here due to date overlap", page.index.min(), "<", latest_updated)
            print("!!! Reduced tx count:", page_newer_filtered.shape[0], 'from', page.shape[0])
            break
    

    new_data = pd.concat(page_updates, axis=0) if page_updates else pd.DataFrame()
    print("")
    print("************************************")
    print("Adding txs: ", new_data.shape[0])
    print("Index type:", new_data.index.dtype)
    print("************************************")
    for i, n in new_data.iterrows():
        print("Sold:", n["baller_id"], f"${n['price']}", "*****" if n["price"] >= 3400 else "")
    print("************************************")
    print("")
    
    # add to old data df
    result = pd.concat([new_data, df], axis=0)
    result.index.name = 'datetime'
    result.to_csv(HISTORY_FILE, index=True)

    return result


if __name__ == '__main__':
    result = update_sales()
    print(result.shape)
    print(result.columns)

### to run this update `poetry run python -m ballerz.update_sales`
