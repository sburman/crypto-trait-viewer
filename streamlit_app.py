import streamlit as st
import pandas as pd
import numpy as np

from os import listdir
from os.path import isfile, join

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
    st.dataframe(data=_, height=800)
