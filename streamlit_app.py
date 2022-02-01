import streamlit as st
import pandas as pd
import numpy as np

from os import listdir
from os.path import isfile, join

import altair as alt

import ballerz.sales as sales
import ballerz.listings as listings
import ballerz.sales_history as sales_history
from ballerz.helpers import BALLERZ

from streamlit_autorefresh import st_autorefresh

# root_dir = './data'
# onlyfiles = [f for f in listdir(root_dir) if isfile(join(root_dir, f))]

# file_list = {}
# for f in onlyfiles:
#     name = f[0:-4]
#     file_list[name] = f"{root_dir}/{f}"

st.set_page_config(page_title="Ballerz", layout="wide")

function_choice = st.sidebar.selectbox(
    "Choose supported function:",
    ["Sales Analysis", "Live Sales", "Live Listings", "Twitter Template"]
)

if function_choice == "Live Listings":
    listings.display()
    st_autorefresh(interval=30*1000, key="listingscounter")
elif function_choice == "Live Sales":
    sales.display()
    st_autorefresh(interval=30*1000, key="salescounter")
elif function_choice == "Sales Analysis":
    sales_history.display()
elif function_choice == "Twitter Template":
    baller_id = st.text_input("Id", value="")
    baller_price = st.text_input("Price", value="")
    #do something with id
    if not baller_id:
        st.caption("Enter a baller")
    else:
        baller = BALLERZ[BALLERZ["baller_id"] == int(float(baller_id))].iloc[0]
        st.markdown(f""":fire::fire::fire: #BallerzNation sale alert

    Baller #{baller["baller_id"]} sells for ${baller_price}

    * Combo rank: {baller['Combo Rank']}
    * Trait rank: {baller['Trait Rank']}
    * Skill rank: {baller['Skill Rank']}

    More about this baller: https://ballerz.info/?ballerz-id={baller['baller_id']}

    Own your very own baller at the @BALLERZ_NFT marketplace: https://ongaia.com/ballerz""")

        st.image(baller["Image"])

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


