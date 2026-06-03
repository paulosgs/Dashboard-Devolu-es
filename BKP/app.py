import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Dashboard Devoluções",
    page_icon="📊",
    layout="wide"
)

# =====================
# LEITURA DOS DADOS
# =====================

ARQUIVO = "dados/Analise_Conta_Corrente.xlsx"

df = pd.read_excel(ARQUIVO)

# =====================
# TRATAMENTO
# =====================

campos_numericos = [
    'CONTA_CORRENTE',
    'VLVENDA',
    'TV5',
    'TV11',
    'ACIMA_TABELA',
    'DEV_GRANDES_REDES',
    'DEMAIS_DEV'
]

for coluna in campos_numericos:
    if coluna in df.columns:
        df[coluna] = pd.to_numeric(df[coluna], errors='coerce').fillna(0)

# DEVOLUÇÃO CORRETA

df["DEV_TOTAL"] = (
    df["DEV_GRANDES_REDES"] +
    df["DEMAIS_DEV"]
)

# Percentuais sobre venda

df["PERC_GRANDES_REDES"] = (
    df["DEV_GRANDES_REDES"] / df["VLVENDA"]
).fillna(0) * 100

df["PERC_DEMAIS_DEV"] = (
    df["DEMAIS_DEV"] / df["VLVENDA"]
).fillna(0) * 100

df["PERC_TROCAS"] = (
    df["TV11"] / df["VLVENDA"]
).fillna(0) * 100

df["PERC_BONIFICACAO"] = (
    df["TV5"] / df["VLVENDA"]
).fillna(0) * 100

# %

df["PERC_DEV"] = (
    (df["DEV_TOTAL"] / df["VLVENDA"])
    .replace([float("inf")], 0)
    .fillna(0)
) * 100

# =====================
# SIDEBAR
# =====================

st.sidebar.header("Filtros")

gerente = st.sidebar.multiselect(
    "Gerente",
    sorted(df["NOMEGERENTE"].dropna().unique())
)

supervisor = st.sidebar.multiselect(
    "Supervisor",
    sorted(df["SUPERVISOR"].dropna().unique())
)

rca = st.sidebar.multiselect(
    "RCA",
    sorted(df["RCA"].dropna().unique())
)

filtro = df.copy()

if gerente:
    filtro = filtro[filtro["NOMEGERENTE"].isin(gerente)]

if supervisor:
    filtro = filtro[filtro["SUPERVISOR"].isin(supervisor)]

if rca:
    filtro = filtro[filtro["RCA"].isin(rca)]

# =====================
# KPIs
# =====================

st.title("📊 Dashboard de Devoluções")

vendas = filtro["VLVENDA"].sum()
devolucoes = filtro["DEV_TOTAL"].sum()
trocas = filtro["TV11"].sum()

perc_dev = (
    (devolucoes / vendas) * 100
    if vendas > 0 else 0
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Vendas",
    f"R$ {vendas:,.2f}"
)

col2.metric(
    "Devoluções",
    f"R$ {devolucoes:,.2f}"
)

col3.metric(
    "Trocas",
    f"R$ {trocas:,.2f}"
)

col4.metric(
    "% Devolução",
    f"{perc_dev:.2f}%"
)

st.divider()

# =====================
# DEVOLUÇÕES POR GERENTE
# =====================

ger = (
    filtro
    .groupby("NOMEGERENTE")["DEV_TOTAL"]
    .sum()
    .reset_index()
    .sort_values(
        "DEV_TOTAL",
        ascending=False
    )
)

fig_ger = px.bar(
    ger,
    x="NOMEGERENTE",
    y="DEV_TOTAL",
    title="Devoluções por Gerente",
    text_auto=".2s"
)

st.plotly_chart(
    fig_ger,
    use_container_width=True
)

# =====================
# DEVOLUÇÕES POR SUPERVISOR
# =====================

sup = (
    filtro
    .groupby("SUPERVISOR")["DEV_TOTAL"]
    .sum()
    .reset_index()
    .sort_values(
        "DEV_TOTAL",
        ascending=False
    )
)

fig_sup = px.bar(
    sup,
    x="SUPERVISOR",
    y="DEV_TOTAL",
    title="Devoluções por Supervisor",
    text_auto=".2s"
)

st.plotly_chart(
    fig_sup,
    use_container_width=True
)

# =====================
# TOP RCA
# =====================

top_rca = (
    filtro[
        [
            "RCA",
            "VLVENDA",
            "DEV_TOTAL",
            "PERC_DEV"
        ]
    ]
    .sort_values(
        "DEV_TOTAL",
        ascending=False
    )
    .head(20)
)

st.subheader(
    "Top 20 RCA com Maiores Devoluções"
)

st.dataframe(
    top_rca,
    use_container_width=True
)

# =====================
# PARETO
# =====================

pareto = (
    filtro
    .groupby("RCA")["DEV_TOTAL"]
    .sum()
    .reset_index()
)

pareto = pareto.sort_values(
    "DEV_TOTAL",
    ascending=False
)

pareto["ACUMULADO"] = (
    pareto["DEV_TOTAL"].cumsum()
)

pareto["PERC_ACUM"] = (
    pareto["ACUMULADO"]
    / pareto["DEV_TOTAL"].sum()
) * 100

fig_pareto = px.bar(
    pareto.head(20),
    x="RCA",
    y="DEV_TOTAL",
    title="Pareto das Devoluções"
)

st.plotly_chart(
    fig_pareto,
    use_container_width=True
)

# =====================
# TABELA ANALÍTICA
# =====================

st.subheader("Base Analítica")

st.dataframe(
    filtro[
        [
            "NOMEGERENTE",
            "SUPERVISOR",
            "RCA",
            "VLVENDA",
            "DEV_TOTAL",
            "TV11",
            "PERC_DEV",
            "CONTA_CORRENTE"
        ]
    ],
    use_container_width=True
)
# ==========================================
# RANKING GRANDES REDES
# ==========================================

st.subheader("🏢 Ranking - Grandes Redes")

ranking_grandes = (
    filtro.groupby("RCA")
    .agg({
        "DEV_GRANDES_REDES":"sum",
        "VLVENDA":"sum"
    })
    .reset_index()
)

ranking_grandes["% SOBRE VENDA"] = (
    ranking_grandes["DEV_GRANDES_REDES"]
    / ranking_grandes["VLVENDA"]
) * 100

ranking_grandes = ranking_grandes.sort_values(
    "DEV_GRANDES_REDES",
    ascending=False
)

st.dataframe(
    ranking_grandes.head(20),
    use_container_width=True
)

# ==========================================
# RANKING DEVOLUÇÕES NORMAIS
# ==========================================

st.subheader("👥 Ranking - Devoluções Normais")

ranking_normal = (
    filtro.groupby("RCA")
    .agg({
        "DEMAIS_DEV":"sum",
        "VLVENDA":"sum"
    })
    .reset_index()
)

ranking_normal["% SOBRE VENDA"] = (
    ranking_normal["DEMAIS_DEV"]
    / ranking_normal["VLVENDA"]
) * 100

ranking_normal = ranking_normal.sort_values(
    "DEMAIS_DEV",
    ascending=False
)

st.dataframe(
    ranking_normal.head(20),
    use_container_width=True
)

# ==========================================
# RANKING TROCAS
# ==========================================

st.subheader("🔄 Ranking - Trocas")

ranking_trocas = (
    filtro.groupby("RCA")
    .agg({
        "TV11":"sum",
        "VLVENDA":"sum"
    })
    .reset_index()
)

ranking_trocas["% SOBRE VENDA"] = (
    ranking_trocas["TV11"]
    / ranking_trocas["VLVENDA"]
) * 100

ranking_trocas = ranking_trocas.sort_values(
    "TV11",
    ascending=False
)

st.dataframe(
    ranking_trocas.head(20),
    use_container_width=True
)

# ==========================================
# RANKING BONIFICAÇÕES
# ==========================================

st.subheader("🎁 Ranking - Bonificações")

ranking_boni = (
    filtro.groupby("RCA")
    .agg({
        "TV5":"sum",
        "VLVENDA":"sum"
    })
    .reset_index()
)

ranking_boni["% SOBRE VENDA"] = (
    ranking_boni["TV5"]
    / ranking_boni["VLVENDA"]
) * 100

ranking_boni = ranking_boni.sort_values(
    "TV5",
    ascending=False
)

st.dataframe(
    ranking_boni.head(20),
    use_container_width=True
)