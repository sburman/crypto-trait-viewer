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

print(file_list)

file_choice = st.sidebar.selectbox(
    "How would you like to be contacted?",
    file_list.keys()
)

st.title(file_choice)

file_to_load = file_list[file_choice]

st.header(f"Loading: {file_to_load}")

df = pd.read_csv(file_to_load)[["category", "trait", "count", "rarity_score"]]

top = df.sort_values(['rarity_score'], ascending=False).head(30)
st.dataframe(data=top, height=1000)

