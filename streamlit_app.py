import streamlit as st
import pandas as pd
import numpy as np

from os import listdir
from os.path import isfile, join

import altair as alt

root_dir = './data'
onlyfiles = [f for f in listdir(root_dir) if isfile(join(root_dir, f))]

file_list = {}
for f in onlyfiles:
    name = f[0:-4]
    file_list[name] = f"{root_dir}/{f}"

file_choice = st.sidebar.selectbox(
    "Choose supported project:",
    file_list.keys()
)

st.title(file_choice)

file_to_load = file_list[file_choice]
df = pd.read_csv(file_to_load)[["category", "trait", "count", "rarity_score"]]

cat_list = ["All"] + list(df["category"].unique())

cat_selected = st.sidebar.selectbox(
    "Select a single category:",
    cat_list
)

if cat_selected is None or cat_selected == "All":
    _ = df.sort_values(['rarity_score'], ascending=False)
    st.dataframe(data=_, height=800)
else:
    _ = df[df["category"] == cat_selected].sort_values(['rarity_score'], ascending=False)

    bar = alt.Chart(_).mark_bar().encode(
        x='trait',
        y='rarity_score'
    )

    rule = alt.Chart(_).mark_rule(color='red').encode(
            y='mean(rarity_score)'
    )

    chart = (bar + rule).properties(width=600)
    st.altair_chart(chart, use_container_width=False)

    st.table(data=_)


