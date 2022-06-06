from matplotlib.axis import XAxis
import streamlit as st
import pandas as pd
from gsheetsdb import connect
import plotly_express as px

st.set_page_config(page_title="EF 517",
     page_icon="chart_with_upwards_trend",
     layout="wide"
 )
# Create a connection object.
conn = connect()
# Perform SQL query on the Google Sheet.
# Uses st.cache to only rerun when the query changes or after 10 min.
def run_query(query):
    rows = conn.execute(query, headers=1)
    rows = rows.fetchall()
    return rows
sheet_url = st.secrets["public_gsheets_url"]
rows = run_query(f'SELECT * FROM "{sheet_url}"')
#Converting google sheet to pandas Data Frame
df = pd.DataFrame(rows)

st.header("517 - Visconde de Albuquerque")

st.sidebar.header('Selecione os filtros')
function = st.sidebar.multiselect(
    "Selecione a função:",
    options=df["Função"].unique(),
    default=df["Função"].unique()
)
time = st.sidebar.multiselect(
    "Selecione o horário:",
    options=df["Horário"].unique(),
    default=df["Horário"].unique()
)

df_selection = df.query(
    "Função == @function & Horário == @time"
)
df_selection = df_selection.sort_values(by="V0")
fig_zero = px.bar(
    df_selection,
    title="<b>V0 por Colaborador</b>",
    x="V0",
    y="Colaborador",
    color_discrete_sequence=["#0083B8"]*len(df_selection)
)
fig_zero.update_layout(
    plot_bgcolor ="rgba(0,0,0,0)",
    xaxis=dict(title="V0 em R$")
)

combos_gen = df[df["Função"]=="Balconista"].sort_values(by="Combos")
fig_combos = px.bar(
    combos_gen,
    title="<b>Combos L3P2 por Colaborador</b>",
    x="Combos",
    y="Colaborador",
    color_discrete_sequence=["#FECB52"]*len(combos_gen)
)
fig_combos.update_layout(
    plot_bgcolor ="rgba(0,0,0,0)",
    xaxis=dict(title="Nº de combos")
)
be_better = df[df["Função"]=="Caixa"].sort_values(by="BeBetter")

fig_bb = px.bar(
    be_better,
    title="<b>Marca própria por Colaborador</b>",
    x="BeBetter",
    y="Colaborador",
    color_discrete_sequence=["#FF9900"]*len(be_better)
)
fig_bb.update_layout(
    plot_bgcolor ="rgba(0,0,0,0)",
    xaxis=dict(title="Nº de combos")
)
df_selection = df_selection.sort_values(by="Desafio")
fig_desafio = px.bar(
    df_selection,
    title="<b>Desafio do dia por Colaborador</b>",
    x="Desafio",
    y="Colaborador",
    color_discrete_sequence=["#782AB6"]*len(df_selection)
)
fig_desafio.update_layout(
    plot_bgcolor ="rgba(0,0,0,0)",
    xaxis=dict(title="Nº de itens vendidos")
)
left_column , right_column = st.columns(2)
left_column.plotly_chart(fig_combos, use_container_width=True)
left_column.plotly_chart(fig_bb, use_container_width=True)
right_column.plotly_chart(fig_zero, use_container_width=True)
right_column.plotly_chart(fig_desafio, use_container_width=True)

