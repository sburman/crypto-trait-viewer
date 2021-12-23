#!/usr/bin/env python

import datetime
from datetime import datetime, timedelta
    
import pandas as pd

from .sales import *

def load_current_state() -> pd.DataFrame:
    return pd.DataFrame()

FILENAME = './ballerz/ballerz_sales_history.csv'

def update_sales() -> pd.DataFrame:

    df = pd.read_csv(FILENAME, parse_dates=['datetime'])
    print(df.shape)

    d = datetime.datetime.now() - timedelta(days=4)
    latest_updated = df['datetime'].max()
    print("Existing from", df['datetime'].min(), "to", latest_updated)
    
    max_pages = 50
    page_updates = []
    for i in range(1, max_pages + 1):
        
        page = get_raw_df_for_page(i)
        print(f"Page {i} from", page['datetime'].min(), "to", page['datetime'].max())
        page_newer_filtered = page[page['datetime'] > latest_updated]
        page_updates.append(page_newer_filtered)

        # pd.concat(page_updates, axis=0, ignore_index=True).to_csv(f"./ballerz/dump/ballerz_sales_history_{i}.csv", index=False)

        # if we dropped any entries we know we have overlapped the time
        if page.shape[0] != page_newer_filtered.shape[0]:
            print("!!! Stopping here due to date overlap", page['datetime'].min(), "<", latest_updated)
            print("!!! Reduced tx count:", page_newer_filtered.shape[0], 'from', page.shape[0])
            break
    

    new_data = pd.concat(page_updates, axis=0, ignore_index=True) if page_updates else pd.DataFrame()
    print("Adding txs: ", new_data.shape[0])
    
    # add to old data df
    result = pd.concat([new_data, df])
    result.to_csv(FILENAME, index=False)
    print("Completed update: ", new_data.shape[0], "from", result['datetime'].min(), "to", result['datetime'].max())

    return result


if __name__ == '__main__':
    result = update_sales()
    print(result.shape)
    print(result.columns)

### to run this update `poetry run python -m ballerz.update_sales`
