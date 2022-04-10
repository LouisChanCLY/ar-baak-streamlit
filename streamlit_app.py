import pandas as pd
import plotly.express as px
import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account

# Create API client.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

# Perform query.
# Uses st.experimental_memo to only rerun when the query changes or after 10 min.
@st.experimental_memo(ttl=5)
def run_query(query):
    query_job = client.query(query)
    rows_raw = query_job.result()
    # Convert to list of dicts. Required for st.experimental_memo to hash the return value.
    df = pd.DataFrame([dict(row) for row in rows_raw])
    return df


df_back_win = run_query(
    "SELECT time, race, horse, MAX(discount) discount FROM `ar-baak.ctb988.3H-220410-back` WHERE win_amount=0 AND race=1 GROUP BY time, race, horse"
)
df_back_place = run_query(
    "SELECT time, race, horse, MAX(discount) discount FROM `ar-baak.ctb988.3H-220410-back` WHERE place_amount=0 AND race=1 GROUP BY time, race, horse"
)

# Print results.
st.title("Win Discount for Race 1")
df_back_win = df_back_win.fillna(method="ffill")
df_back_win_race_1 = pd.pivot_table(
    data=df_back_win[df_back_win["race"] == 1],
    values="discount",
    index="time",
    columns="horse",
    aggfunc="first",
)
columns = df_back_win_race_1.columns
df_back_win_race_1 = df_back_win_race_1.reset_index()
fig = px.line(df_back_win_race_1, x="time", y=columns)
st.plotly_chart(fig, use_container_width=True)

st.title("Place Discount for Race 1")
df_back_place = df_back_place.fillna(method="ffill")
df_back_place_race_1 = pd.pivot_table(
    data=df_back_place[df_back_place["race"] == 1],
    values="discount",
    index="time",
    columns="horse",
    aggfunc="first",
)
columns = df_back_place_race_1.columns
df_back_place_race_1 = df_back_place_race_1.reset_index()
fig = px.line(df_back_place_race_1, x="time", y=columns)
st.plotly_chart(fig, use_container_width=True)
