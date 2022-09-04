import streamlit as st
import pandas as pd
from gsheetsdb import connect
import plotly_express as px
import plotly.graph_objects as go
import datetime

initial_day = datetime.datetime.today().replace(day=1)
current_day = datetime.datetime.today()
days = (current_day - initial_day).days +1

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
#Title
st.header("EF 517")



#Sidebar elements
st.sidebar.header('Selecione os filtros:')
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
st.sidebar.header('Defina as metas:')
meta_combos = st.sidebar.slider(label="Meta de Combos", max_value=10, min_value=1, value=6)
meta_bebetter = st.sidebar.slider(label="Meta de Be Better", max_value=10, min_value=1, value=5)
meta_desafio = st.sidebar.slider(label="Meta de Desafio", max_value=10, min_value=1, value=2)
df_selection = df.query(
    "Função == @function & Horário == @time"
)
#V0 chart
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
#Combos chart
df_combos_gen = df_selection[df_selection["Função"]=="Balconista"].sort_values(by="Combos")
fig_combos = px.bar(
    df_combos_gen,
    title="<b>Combos L3P2 por Colaborador</b>",
    y="Combos",
    x="Colaborador",
    color_discrete_sequence=["#FECB52"]*len(df_combos_gen),
)
fig_combos.add_trace(go.Scatter(y=[meta_combos*days for i in range(len(df_combos_gen.Colaborador))],
    x=df_combos_gen.Colaborador,
    mode="lines",
    showlegend=False,
    name="Meta",
    line = dict(color="#86CE00")
    ))
fig_combos.update_layout(
    plot_bgcolor ="rgba(0,0,0,0)",
    xaxis=dict(title="Colaborador"),
    yaxis = dict(title="Nº de Combos")
)
#Be Better chart
df_be_better = df_selection[df_selection["Função"]=="Caixa"].sort_values(by="BeBetter")
fig_bb = px.bar(
    df_be_better,
    title="<b>Marca própria por Colaborador</b>",
    y="BeBetter",
    x="Colaborador",
    color_discrete_sequence=["#FF9900"]*len(df_be_better)
)
fig_bb.add_trace(go.Scatter(y=[meta_bebetter*days for i in range(len(df_be_better.Colaborador))],
    x=df.Colaborador,
    mode="lines",
    showlegend=False,
    name="Meta",
    line = dict(color="#86CE00")
    ))
fig_bb.update_layout(
    plot_bgcolor ="rgba(0,0,0,0)",
    xaxis=dict(title="Colaborador"),
    yaxis = dict(title="Nº de itens Be Better")
)
#Desafio chart
df_selection = df_selection.sort_values(by="Desafio")
df_desafio = df_selection[df_selection["Função"]!="Outros"].sort_values(by="Desafio")
fig_desafio = px.bar(
    df_desafio,
    title="<b>Desafio do dia por Colaborador</b>",
    x="Desafio",
    y="Colaborador",
    color_discrete_sequence=["#782AB6"]*len(df_desafio)
)
fig_desafio.add_trace(go.Scatter(x=[meta_desafio*days for i in range(len(df_desafio.Colaborador))],
    y=df_desafio.Colaborador,
    mode="lines",
    showlegend=False,
    name="Meta",
    line = dict(color="#86CE00")
    ))
fig_desafio.update_layout(
    plot_bgcolor ="rgba(0,0,0,0)",
    xaxis=dict(title="Nº de itens vendidos")
)

left_column , right_column = st.columns(2)
left_column.plotly_chart(fig_combos, use_container_width=True)
left_column.plotly_chart(fig_bb, use_container_width=True)
right_column.plotly_chart(fig_zero, use_container_width=True)
right_column.plotly_chart(fig_desafio, use_container_width=True)

# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)