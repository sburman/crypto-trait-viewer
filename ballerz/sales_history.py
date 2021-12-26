import streamlit as st

import altair as alt
import arrow
import datetime
import json
import pandas as pd
import requests

from typing import Any

from .helpers import *

def human_format(num):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    # add more suffixes if you need them
    return '$%.0f%s' % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])

def display() -> Any:
    st.title("Ballerz Salez History")

    df = pd.read_csv(HISTORY_FILE, index_col='datetime')
    df.index = df.index.astype('datetime64[ns]')
    df = df.join(BALLERZ, on="baller_id", how="left", rsuffix="b_")

    selected_view = st.sidebar.selectbox("Select view", ["Timeline", "Trait Analysis"])

    # some display touch ups to the df
    df['combo_size'] = 10_000 - df['combo']
    df['link'] = df['baller_id'].apply(lambda x: f"https://ballerz.info/?ballerz-id={x}")
    df['ago'] = df['timestamp'].apply(lambda x: arrow.get(int(x)).humanize())

    most_recent = df.index.max()
    
    hours_24 = most_recent - datetime.timedelta(days=1)
    hours_24_sales = df[df.index > hours_24]
    
    hours_48 = most_recent - datetime.timedelta(days=2)
    hours_48_sales = df[df.index > hours_48]

    currency_format = "${:0.0f}"

    col1, col2, col3 = st.columns(3)
    col1.metric(f"Overall Sale Count (updated {arrow.get(most_recent).humanize()})", df.shape[0])
    col2.metric(f"Average Sale", currency_format.format(df['price'].mean()))
    col3.metric(f"Total Sales", human_format(df['price'].sum()))
    
    col1, col2, col3 = st.columns(3)
    col1.metric(f"24hr Sale Count", hours_24_sales.shape[0])
    col2.metric(f"24hr Average Sale", currency_format.format(hours_24_sales['price'].mean()))
    col3.metric(f"24hr Total Sales", human_format(hours_24_sales['price'].sum()))

    col1, col2, col3 = st.columns(3)
    col1.metric(f"48hr Sale Count", hours_48_sales.shape[0])
    col2.metric(f"48hr Average Sale", currency_format.format(hours_48_sales['price'].mean()))
    col3.metric(f"48hr Total Sales", human_format(hours_48_sales['price'].sum()))

    # col2.metric(f"Last 24hr sales", hours_24_sales)
    # col3.metric(f"Previous 24hr sales", hours_48_sales - hours_24_sales)
    
    days_history = st.sidebar.select_slider("Show number of days", options=[1, 2, 3, 4, 5, 6, 7], value=3)
    show_from = most_recent - datetime.timedelta(days=days_history)
    df = df[df.index > show_from]

    max_price = st.sidebar.slider("Filter max price", 0, int(df["price"].max()), 5000)

    df['time_axis'] = df.index

    if selected_view == "Timeline":

        # selected_category = st.sidebar.selectbox(
        #     "Color highlighter:",
        #     ["Role", "Body", "Team", "Gender"]
        # )

        c = alt.Chart(df).mark_circle().encode(
            x=alt.X('time_axis',
                scale=alt.Scale(zero=False),
                axis=alt.Axis(title="Time", format='%b %d %H:%M')
            ),
            y=alt.X(
                'price',
                scale=alt.Scale(domain=(5, max_price), clamp=True),
                axis=alt.Axis(title="Price ($USD)")),
            size=alt.Size('combo_size', legend=None),
            # color=alt.Color(selected_category, legend=None),
            href='link',
            tooltip=['baller_id', 'price', 'ago', 'combo', 'rarity', 'skill']
        ).properties(
            height=1000
        )

        # line = c.transform_loess('time_axis', 'price').mark_line()

        st.altair_chart(c, use_container_width=True)

    elif selected_view == "Trait Analysis":

        selected_category = st.sidebar.selectbox(
            "Analysis category:",
            ["Role", "Body", "Team", "Gender"]
        )

        stripplot = alt.Chart(df, width=50).mark_circle(size=20).encode(
            x=alt.X(
                'jitter:Q',
                title=None,
                axis=alt.Axis(values=[0], ticks=True, grid=False, labels=False),
                scale=alt.Scale(),
            ),
            y=alt.Y('price', scale=alt.Scale(domain=(5, max_price), clamp=True)),
            color=alt.Color(selected_category, legend=None),
            column=alt.Column(
                selected_category,
                header=alt.Header(
                    labelAngle=-90,
                    title=None,
                    labelAnchor="middle",
                    labelAlign='left',
                    labelPadding=3,
                ),
            ),
        ).transform_calculate(
            # Generate Gaussian jitter with a Box-Muller transform
            jitter='sqrt(-2*log(random()))*cos(2*PI*random())'
        ).configure_facet(
            spacing=0
        ).configure_view(
            stroke=None
        ).properties(
            height=800
        )

        st.altair_chart(stripplot)
