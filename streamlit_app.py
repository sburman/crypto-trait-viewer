import streamlit as st
import pandas as pd
import numpy as np

from os import listdir
from os.path import isfile, join

import altair as alt

import ballerz.helpers as helpers

# root_dir = './data'
# onlyfiles = [f for f in listdir(root_dir) if isfile(join(root_dir, f))]

# file_list = {}
# for f in onlyfiles:
#     name = f[0:-4]
#     file_list[name] = f"{root_dir}/{f}"

st.set_page_config(page_title="Ballerz", layout="wide")

function_choice = "Recent Sales"
#  st.sidebar.selectbox(
#     "Choose supported function:",
#     ["Recent Sales"]
# )

if function_choice == "Recent Sales":
    st.title("Ballerz Recent Salez")

    page_choice = st.sidebar.selectbox('Page?', [1, 2, 3, 4, 5])

    df = helpers.get_sales_df_for_page(page_choice)
    st.write(df, unsafe_allow_html=True)
else:
    st.title("Nothing to do. Select a function.")

# file_to_load = file_list[file_choice]
# df = pd.read_csv(file_to_load)[["category", "trait", "count", "rarity_score"]]

# cat_list = ["All"] + list(df["category"].unique())

# cat_selected = st.sidebar.selectbox(
#     "Select a single category:",
#     cat_list
# )

# if cat_selected is None or cat_selected == "All":
#     st.title(file_choice)
#     _ = df.sort_values(['rarity_score'], ascending=False)
#     st.dataframe(data=_, height=800)
# else:
#     st.title(file_choice + " - " + cat_selected)
#     _ = df[df["category"] == cat_selected].sort_values(['rarity_score'], ascending=False)

#     bar = alt.Chart(_).mark_bar().encode(
#         x='trait',
#         y='rarity_score'
#     )

#     rule = alt.Chart(_).mark_rule(color='red').encode(
#             y='mean(rarity_score)'
#     )

#     chart = (bar + rule).properties(width=600)
#     st.altair_chart(chart, use_container_width=False)

#     st.table(data=_)


