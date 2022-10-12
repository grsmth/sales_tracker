import streamlit as st
import pandas as pd
from gsheetsdb import connect
import plotly_express as px
import plotly.graph_objects as go
import datetime
import calendar

initial_day = datetime.datetime.today().replace(day=1)
current_day = datetime.datetime.today()
days = (current_day - initial_day).days +1
daysInMonth = calendar.monthrange(initial_day.year, initial_day.month)[1]

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
sheet2_url = st.secrets["public_gsheets2_url"]
rows = run_query(f'SELECT * FROM "{sheet_url}"')
time_serie = run_query(f'SELECT * FROM "{sheet2_url}"')
#Converting google sheet to pandas Data Frame
df = pd.DataFrame(rows)
ts_df = pd.DataFrame(time_serie)
#Processing 2nd sheet
ts_df['_0'] = ts_df['_0'].dt.date

#Title
st.header("EF 517")
st.subheader("Destaques")

#V0 chart
df_selection = df.sort_values(by="V0",ignore_index=True, ascending=False)
fig_zero = px.bar(
    df_selection,
    title="<b>V0</b>",
    x="V0",
    y="Colaborador",
    color_discrete_sequence=["#0083B8"]*len(df_selection)
)
fig_zero.update_layout(
    plot_bgcolor ="rgba(0,0,0,0)",
    xaxis=dict(title="V0 em R$")
)
#Combos chart
df_combos_gen = df_selection[df_selection["Função"]=="Balconista"].sort_values(by="Combos",ignore_index=True, ascending=False)
fig_combos = px.bar(
    df_combos_gen,
    title="<b>Combos L3P2</b>",
    y="Combos",
    x="Colaborador",
    color_discrete_sequence=["#FECB52"]*len(df_combos_gen),
)
fig_combos.add_trace(go.Scatter(y=[6*days for i in range(len(df_combos_gen.Colaborador))],
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
df_be_better = df_selection[df_selection["Função"]=="Caixa"].sort_values(by="BeBetter",ignore_index=True, ascending=False)
fig_bb = px.bar(
    df_be_better,
    title="<b>Marca própria por Colaborador</b>",
    y="BeBetter",
    x="Colaborador",
    color_discrete_sequence=["#FF9900"]*len(df_be_better)
)
fig_bb.add_trace(go.Scatter(y=[6*days for i in range(len(df_be_better.Colaborador))],
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
df_desafio = df_selection.sort_values(by="Desafio")
df_desafio = df_desafio[df_desafio["Função"]!="Outros"].sort_values(by="Desafio",ignore_index=True, ascending=False)
fig_desafio = px.bar(
    df_desafio,
    title="<b>Fatiamento estratégico</b>",
    x="Desafio",
    y="Colaborador",
    color_discrete_sequence=["#782AB6"]*len(df_desafio)
)
fig_desafio.add_trace(go.Scatter(x=[3*days for i in range(len(df_desafio.Colaborador))],
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
#Frequency chart
fig_frequency = px.histogram(ts_df, x="_0", color="Colaborador", nbins=daysInMonth,
    title="<b>Frequência</b>",
    labels={"_0":"Dia"},
    color_discrete_sequence=px.colors.qualitative.Vivid)
fig_frequency.update_layout(
    plot_bgcolor ="rgba(0,0,0,0)"
)

#KPI's
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric(
    label = "V0: {}".format(df_selection["Colaborador"][0]),
    value = df_selection["V0"][0],
    delta = "{:0.2f}".format(df_selection["V0"][0]/df_selection["V0"][1]),
)
kpi2.metric(
    label = "Combos: {}".format(df_combos_gen["Colaborador"][0]),
    value = df_combos_gen["Combos"][0],
    delta = "{:0.2f}".format(df_combos_gen["Combos"][0]/df_combos_gen["Combos"][1])
)
kpi3.metric(
    label = "Desfio: {}".format(df_desafio["Colaborador"][0]),
    value = df_desafio["Desafio"][0],
    delta = "{:0.2f}".format(df_desafio["Desafio"][0]/df_desafio["Desafio"][1])
)
left_column , right_column = st.columns(2)
left_column.plotly_chart(fig_combos)
left_column.plotly_chart(fig_zero)
right_column.plotly_chart(fig_desafio)
right_column.plotly_chart(fig_frequency)

# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)