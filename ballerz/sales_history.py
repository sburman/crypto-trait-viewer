import streamlit as st

import altair as alt
import arrow
import datetime
import json
import pandas as pd
import requests

from typing import Any

from .helpers import *

def display() -> Any:
    st.title("Ballerz Salez History")

    df = pd.read_csv(HISTORY_FILE, parse_dates=['datetime'])
    df = pd.merge(df, BALLERZ, on="baller_id", how="left")

    # st.write(list(df.columns))

    # some display touch ups to the df
    df['time_axis'] = df['timestamp'].apply(lambda x: arrow.get(x).datetime)
    df['combo_size'] = 10_000 - df['combo']
    df['link'] = df['baller_id'].apply(lambda x: f"https://ballerz.info/?ballerz-id={x}")
    df['ago'] = df['timestamp'].apply(lambda x: arrow.get(int(x)).humanize())

    most_recent = arrow.get(int(df['timestamp'].max()))
    
    hours_24 = show_from = most_recent.shift(days=-1)
    hours_24_sales = df[df['time_axis'] > hours_24.datetime].shape[0]
    
    hours_48 = show_from = most_recent.shift(days=-2)
    hours_48_sales = df[df['time_axis'] > hours_48.datetime].shape[0]


    col1, col2, col3 = st.columns(3)
    col1.metric(f"Total Sales (updated {most_recent.humanize()})", df.shape[0])
    col2.metric(f"Last 24hr sales", hours_24_sales)
    col3.metric(f"Previous 24hr sales", hours_48_sales - hours_24_sales)
    
    days_history = st.sidebar.select_slider("Show number of days", options=[1, 2, 3, 4, 5, 6, 7], value=1)
    max_price = st.sidebar.slider("Filter max price", 0, int(df["price"].max()), 10000)
    show_from = most_recent.shift(days=(0 - days_history))

    df = df[df['time_axis'] > show_from.datetime]
    df = df[df['price'] <= max_price]

    colour = st.sidebar.selectbox(
        "Color highlighter:",
        ["Role", "Body", "Team", "Gender"]
    )

    c = alt.Chart(df).mark_point().encode(
        x=alt.X('time_axis',
            scale=alt.Scale(zero=False),
            axis=alt.Axis(title="Time", format='%b %d %H:%M')
        ),
        y=alt.X('price', axis=alt.Axis(title="Price ($USD)")),
        size=alt.Size('combo_size', legend=None),
        color=colour,
        href='link',
        tooltip=['baller_id', 'price', 'ago', 'combo', 'rarity', 'skill']
    ).properties(
        height=1000
    ).interactive()

    st.altair_chart(c, use_container_width=True)
