import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image

# ==========================================
# CORES
# ==========================================

AZUL = "#00BFFF"
AMARELO = "#FDBE2D"
FUNDO = "#08111f"
CARD = "#111c2e"
VERDE = "#00CC96"
VERMELHO = "#EF553B"

# ==========================================
# CONFIGURAÇÃO
# ==========================================

st.set_page_config(
    page_title="Dashboard Devoluções",
    page_icon="📊",
    layout="wide"
)

# ==========================================
# FUNÇÕES
# ==========================================

def moeda(valor):
    return (
        f"R$ {abs(valor):,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

def percentual(valor):
    return (
        f"{valor:.2f}%"
        .replace(".", ",")
    )

# ==========================================
# CSS
# ==========================================

st.markdown(
f"""
<style>

.stApp {{
    background-color:{FUNDO};
}}

section[data-testid="stSidebar"] {{
    background-color:#0d1726;
}}

h1,h2,h3,h4 {{
    color:white;
}}

[data-testid="stMetric"] {{
    background:{CARD};
    border:1px solid {AZUL};
    border-radius:15px;
    padding:15px;
    box-shadow:0 0 10px rgba(0,191,255,.3);
}}

</style>
""",
unsafe_allow_html=True
)

# ==========================================
# UPLOAD
# ==========================================

st.sidebar.markdown("## 📤 Upload da Planilha - Rotina 8079")

arquivo = st.sidebar.file_uploader(
    "Selecione a planilha",
    type=["xlsx"]
)

if arquivo is None:

    st.info(
        "Abra a Rotina 8079 no Winthor e Salve a planilha em formato .xlsx e faça upload da planilha para gerar o dashboard."
    )

    st.stop()

# ==========================================
# LEITURA
# ==========================================

@st.cache_data
def carregar(arquivo):

    df = pd.read_excel(arquivo)

    campos = [
        "CONTA_CORRENTE",
        "VLVENDA",
        "TV5",
        "TV11",
        "ACIMA_TABELA",
        "DEV_GRANDES_REDES",
        "DEMAIS_DEV"
    ]

    for campo in campos:

        if campo in df.columns:

            df[campo] = pd.to_numeric(
                df[campo],
                errors="coerce"
            ).fillna(0)

    obrigatorios = [
        "ACIMA_TABELA",
        "DEV_GRANDES_REDES",
        "DEMAIS_DEV",
        "TV11",
        "TV5"
    ]

    for campo in obrigatorios:

        if campo not in df.columns:

            df[campo] = 0

    df["DEV_TOTAL"] = (
        df["DEV_GRANDES_REDES"]
        +
        df["DEMAIS_DEV"]
    )

    df["IMPACTO_FINANCEIRO"] = (
        df["DEV_TOTAL"].abs()
        +
        df["TV11"].abs()
        +
        df["TV5"].abs()
        -
        df["ACIMA_TABELA"].abs()
    )

    return df

df = carregar(arquivo)

st.sidebar.success(
    f"Arquivo: {arquivo.name}"
)

# ==========================================
# FILTROS
# ==========================================

st.sidebar.title("🎯 Filtros")

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
    filtro = filtro[
        filtro["NOMEGERENTE"].isin(gerente)
    ]

if supervisor:
    filtro = filtro[
        filtro["SUPERVISOR"].isin(supervisor)
    ]

if rca:
    filtro = filtro[
        filtro["RCA"].isin(rca)
    ]

# ==========================================
# CABEÇALHO
# ==========================================

col1, col2 = st.columns([4,1])

with col1:

    st.title(
        "📊 DASHBOARD DE DEVOLUÇÕES"
    )

with col2:

    try:

        logo = Image.open(
            "assets/Logo Distrinorte Branca.png"
        )

        st.image(
            logo,
            width=320
        )

    except:

        st.warning(
            "Logo não encontrada."
        )

# ==========================================
# INDICADORES
# ==========================================

vendas = abs(
    filtro["VLVENDA"].sum()
)

dev_total = abs(
    filtro["DEV_TOTAL"].sum()
)

grandes_redes = abs(
    filtro["DEV_GRANDES_REDES"].sum()
)

dev_normais = abs(
    filtro["DEMAIS_DEV"].sum()
)

trocas = abs(
    filtro["TV11"].sum()
)

bonificacoes = abs(
    filtro["TV5"].sum()
)

acima_tabela = abs(
    filtro["ACIMA_TABELA"].sum()
)

impacto = abs(
    filtro["IMPACTO_FINANCEIRO"].sum()
)

perc_dev = (
    (dev_total / vendas) * 100
    if vendas > 0
    else 0
)

# ==========================================
# META
# ==========================================

META_DEV = 0.60

status_meta = (
    "🟢 DENTRO DA META"
    if perc_dev <= META_DEV
    else "🔴 ACIMA DA META"
)

# ==========================================
# CARDS LINHA 1
# ==========================================

c1, c2, c3, c4 = st.columns(4)

with c1:

    st.metric(
        "💰 VENDAS",
        moeda(vendas)
    )

with c2:

    st.metric(
        "↩️ DEVOLUÇÕES",
        moeda(dev_total)
    )

with c3:

    st.metric(
        "🏢 GRANDES REDES",
        moeda(grandes_redes)
    )

with c4:

    st.metric(
        "🔄 TROCAS",
        moeda(trocas)
    )

# ==========================================
# CARDS LINHA 2
# ==========================================

c5, c6, c7, c8 = st.columns(4)

with c5:

    st.metric(
        "🎁 BONIFICAÇÕES",
        moeda(bonificacoes)
    )

with c6:

    st.metric(
        "% DEV",
        percentual(perc_dev)
    )

with c7:

    st.metric(
        "📈 ACIMA DA TABELA",
        moeda(acima_tabela)
    )

with c8:

    st.metric(
        "↩️DEV + 🔄TROC + 🎁BNF - 📈ACIM. TAB",
        moeda(impacto)
    )

# ==========================================
# META VISUAL
# ==========================================

if perc_dev <= META_DEV:

    st.success(
        f"""
Meta de Devolução: {percentual(META_DEV)}

Status: {status_meta}
"""
    )

else:

    st.error(
        f"""
Meta de Devolução: {percentual(META_DEV)}

Status: {status_meta}
"""
    )

# ==========================================
# RESUMO EXECUTIVO AUTOMÁTICO
# ==========================================

try:

    pior_rca = (
        filtro.groupby("RCA")
        ["DEV_TOTAL"]
        .sum()
        .abs()
        .idxmax()
    )

    maior_gerente = (
        filtro.groupby("NOMEGERENTE")
        ["DEV_TOTAL"]
        .sum()
        .abs()
        .idxmax()
    )

    maior_supervisor = (
        filtro.groupby("SUPERVISOR")
        ["DEV_TOTAL"]
        .sum()
        .abs()
        .idxmax()
    )

    st.info(
        f"""
📌 PRINCIPAIS DESTAQUES

• RCA com maior devolução: {pior_rca}

• Gerente com maior devolução: {maior_gerente}

• Supervisor com maior devolução: {maior_supervisor}

• Impacto financeiro acumulado: {moeda(impacto)}
"""
    )

except:
    pass

# ==========================================
# ABAS
# ==========================================

aba1, aba2, aba3 = st.tabs(
    [
        "📊 GRÁFICOS DE RESUMO",
        "🏆 RANKINGS",
        "📋 BASE ANALÍTICA"
    ]
)

# ==========================================
# ABA 1 - GRÁFICOS DE RESUMO
# ==========================================

with aba1:

    col1, col2 = st.columns(2)

    # ======================================
    # DONUT
    # ======================================

    with col1:

        composicao = pd.DataFrame({
            "Categoria":[
                "Grandes Redes",
                "Dev. Normais",
                "Trocas",
                "Bonificações",
                "Acima Tabela"
            ],
            "Valor":[
                grandes_redes,
                dev_normais,
                trocas,
                bonificacoes,
                acima_tabela
            ]
        })

        fig_donut = px.pie(
            composicao,
            names="Categoria",
            values="Valor",
            hole=0.72,
            color="Categoria",
            color_discrete_map={
                "Grandes Redes": AZUL,
                "Dev. Normais": AMARELO,
                "Trocas": "#4DA6FF",
                "Bonificações": "#FFE082",
                "Acima Tabela": VERDE
            }
        )

        fig_donut.update_layout(
            template="plotly_dark",
            paper_bgcolor=FUNDO,
            plot_bgcolor=FUNDO,
            height=520
        )

        st.plotly_chart(
            fig_donut,
            use_container_width=True
        )

    # ======================================
    # TOP IMPACTO FINANCEIRO
    # ======================================

    with col2:

        impacto_rca = (
            filtro.groupby("RCA")
            ["IMPACTO_FINANCEIRO"]
            .sum()
            .reset_index()
            .sort_values(
                "IMPACTO_FINANCEIRO",
                ascending=False
            )
            .head(15)
        )

        impacto_rca["RCA_CURTO"] = (
            impacto_rca["RCA"]
            .astype(str)
            .str[:35]
        )

        fig_impacto = px.bar(
            impacto_rca,
            x="IMPACTO_FINANCEIRO",
            y="RCA_CURTO",
            orientation="h",
            title="🏆 Top 15 Impacto Financeiro",
            color_discrete_sequence=[AMARELO]
        )

        fig_impacto.update_traces(
            marker_line_color=AZUL,
            marker_line_width=1.5
        )

        fig_impacto.update_layout(
            template="plotly_dark",
            paper_bgcolor=FUNDO,
            plot_bgcolor=FUNDO,
            height=520,
            yaxis={
                "categoryorder":"total ascending"
            }
        )

        st.plotly_chart(
            fig_impacto,
            use_container_width=True
        )

    st.markdown("---")

    # ======================================
    # PARETO EM LINHA
    # ======================================

    pareto = (
        filtro.groupby("RCA")
        ["DEV_TOTAL"]
        .sum()
        .abs()
        .reset_index()
        .sort_values(
            "DEV_TOTAL",
            ascending=False
        )
    )

    pareto["ACUMULADO"] = (
        pareto["DEV_TOTAL"]
        .cumsum()
    )

    pareto["PERC_ACUM"] = (
        pareto["ACUMULADO"]
        /
        pareto["DEV_TOTAL"].sum()
    ) * 100

    pareto["RCA_CURTO"] = (
        pareto["RCA"]
        .astype(str)
        .str[:25]
    )

    fig_pareto = go.Figure()

    fig_pareto.add_trace(
        go.Scatter(
            x=pareto["RCA_CURTO"],
            y=pareto["DEV_TOTAL"],
            mode="lines+markers",
            line=dict(
                color=AZUL,
                width=3
            ),
            name="Devoluções"
        )
    )

    fig_pareto.add_trace(
        go.Scatter(
            x=pareto["RCA_CURTO"],
            y=pareto["PERC_ACUM"],
            mode="lines+markers",
            yaxis="y2",
            line=dict(
                color=AMARELO,
                width=3
            ),
            name="% Acumulado"
        )
    )

    fig_pareto.update_layout(
        template="plotly_dark",
        paper_bgcolor=FUNDO,
        plot_bgcolor=FUNDO,
        title="Pareto de Devoluções",
        height=550,
        yaxis2=dict(
            overlaying="y",
            side="right",
            range=[0,100]
        )
    )

    st.plotly_chart(
        fig_pareto,
        use_container_width=True
    )

    st.markdown("---")

    # ======================================
    # VENDA X IMPACTO EM LINHA
    # ======================================

    scatter = (
        filtro.groupby("RCA")
        .agg({
            "VLVENDA":"sum",
            "IMPACTO_FINANCEIRO":"sum"
        })
        .reset_index()
        .sort_values("VLVENDA")
    )

    fig_linha = go.Figure()

    fig_linha.add_trace(
        go.Scatter(
            x=scatter["RCA"],
            y=scatter["VLVENDA"],
            mode="lines",
            name="Venda",
            line=dict(
                color=AZUL,
                width=3
            )
        )
    )

    fig_linha.add_trace(
        go.Scatter(
            x=scatter["RCA"],
            y=scatter["IMPACTO_FINANCEIRO"],
            mode="lines",
            name="Impacto",
            line=dict(
                color=AMARELO,
                width=3
            )
        )
    )

    fig_linha.update_layout(
        template="plotly_dark",
        paper_bgcolor=FUNDO,
        plot_bgcolor=FUNDO,
        title="Venda x Impacto Financeiro",
        height=550
    )

    st.plotly_chart(
        fig_linha,
        use_container_width=True
    )

    st.markdown("---")

    # ======================================
    # PARTICIPAÇÃO GERENTES
    # ======================================

    gerentes = (
        filtro.groupby("NOMEGERENTE")
        ["DEV_TOTAL"]
        .sum()
        .abs()
        .reset_index()
    )

    fig_ger = px.pie(
        gerentes,
        names="NOMEGERENTE",
        values="DEV_TOTAL",
        title="Participação das Devoluções por Gerente"
    )

    fig_ger.update_layout(
        template="plotly_dark"
    )

    st.plotly_chart(
        fig_ger,
        use_container_width=True
    )

    # ======================================
    # PARTICIPAÇÃO SUPERVISORES
    # ======================================

    supervisores = (
        filtro.groupby("SUPERVISOR")
        ["DEV_TOTAL"]
        .sum()
        .abs()
        .reset_index()
    )

    fig_sup = px.pie(
        supervisores,
        names="SUPERVISOR",
        values="DEV_TOTAL",
        title="Participação das Devoluções por Supervisor"
    )

    fig_sup.update_layout(
        template="plotly_dark"
    )

    st.plotly_chart(
        fig_sup,
        use_container_width=True
    )

# ==========================================
# ABA 2 - RANKINGS
# ==========================================

with aba2:

    # ======================================
    # TIPO DE ORDENAÇÃO
    # ======================================

    tipo_ordenacao = st.radio(
        "Ordenar Rankings por",
        [
            "Valor total de Devolução",
            "% Sobre Venda"
        ],
        horizontal=True
    )

    # ======================================
    # FUNÇÃO PADRÃO
    # ======================================

    def ranking_rca(campo, titulo):

        base = (
            filtro.groupby("RCA")
            .agg({
                campo: "sum",
                "VLVENDA": "sum"
            })
            .reset_index()
        )

        base[campo] = (
            base[campo]
            .abs()
        )

        base["PERC_NUM"] = (
            base[campo]
            /
            base["VLVENDA"]
        ).fillna(0) * 100

        # ==================================
        # ORDENAÇÃO
        # ==================================

        if tipo_ordenacao == "Valor total de Devolução":

            base = base.sort_values(
                campo,
                ascending=False
            )

        else:

            base = base.sort_values(
                "PERC_NUM",
                ascending=False
            )

        # ==================================
        # FORMATAÇÃO
        # ==================================

        base["VALOR"] = (
            base[campo]
            .apply(moeda)
        )

        base["VENDA"] = (
            base["VLVENDA"]
            .apply(moeda)
        )

        base["% SOBRE VENDA"] = (
            base["PERC_NUM"]
            .apply(percentual)
        )

        base = base[
            [
                "RCA",
                "VALOR",
                "VENDA",
                "% SOBRE VENDA"
            ]
        ]

        st.subheader(titulo)

        st.dataframe(
            base.head(50),
            use_container_width=True,
            hide_index=True
        )

    # ======================================
    # RANKINGS PRINCIPAIS
    # ======================================

    col1, col2 = st.columns(2)

    with col1:

        ranking_rca(
            "DEV_GRANDES_REDES",
            "🏢 RANKING GRANDES REDES"
        )

        ranking_rca(
            "TV11",
            "🔄 RANKING TROCAS"
        )

        ranking_rca(
            "ACIMA_TABELA",
            "📈 RANKING VENDIDO ACIMA DA TABELA"
        )

    with col2:

        ranking_rca(
            "DEMAIS_DEV",
            "👥 RANKING DEVOLUÇÕES NORMAIS"
        )

        ranking_rca(
            "TV5",
            "🎁 RANKING BONIFICAÇÕES"
        )

    st.markdown("---")

    # ======================================
    # TOP IMPACTO FINANCEIRO
    # ======================================

    impacto_rank = (
        filtro.groupby("RCA")
        ["IMPACTO_FINANCEIRO"]
        .sum()
        .abs()
        .reset_index()
        .sort_values(
            "IMPACTO_FINANCEIRO",
            ascending=False
        )
    )

    impacto_rank["VALOR"] = (
        impacto_rank["IMPACTO_FINANCEIRO"]
        .apply(moeda)
    )

    st.subheader(
        "🏆 RANKING IMPACTO FINANCEIRO"
    )

    st.dataframe(
        impacto_rank[
            ["RCA", "VALOR"]
        ].head(20),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

# ======================================
# TOP PIORES ÍNDICES
# ======================================

indice = (
    filtro.groupby("RCA")
    .agg({
        "DEV_TOTAL": "sum",
        "VLVENDA": "sum"
    })
    .reset_index()
)

# ======================================
# ELIMINA RCAS SEM VENDA
# ======================================

indice = indice[
    indice["VLVENDA"] > 0
]

# ======================================
# ELIMINA RCAS INATIVOS
# (AJUSTE SE NECESSÁRIO)
# ======================================

VALOR_MINIMO_VENDA = 50000

indice = indice[
    indice["VLVENDA"] >= VALOR_MINIMO_VENDA
]

# ======================================
# CALCULA PERCENTUAL
# ======================================

indice["PERCENTUAL_NUM"] = (
    indice["DEV_TOTAL"].abs()
    /
    indice["VLVENDA"]
) * 100

# ======================================
# REMOVE DISTORÇÕES
# ======================================

indice = indice[
    indice["PERCENTUAL_NUM"] <= 50
]

# ======================================
# ORDENA
# ======================================

indice = indice.sort_values(
    "PERCENTUAL_NUM",
    ascending=False
)

# ======================================
# FORMATAÇÃO
# ======================================

indice["DEV_TOTAL_FMT"] = (
    indice["DEV_TOTAL"]
    .abs()
    .apply(moeda)
)

indice["VLVENDA_FMT"] = (
    indice["VLVENDA"]
    .apply(moeda)
)

indice["PERCENTUAL"] = (
    indice["PERCENTUAL_NUM"]
    .apply(percentual)
)

# ======================================
# EXIBIÇÃO
# ======================================

st.subheader(
    "🚨 RANKING PIORES ÍNDICES DE DEVOLUÇÃO"
)

st.caption(
    f"Considerando apenas RCAs com vendas acima de {moeda(VALOR_MINIMO_VENDA)}"
)

st.dataframe(
    indice[
        [
            "RCA",
            "DEV_TOTAL_FMT",
            "VLVENDA_FMT",
            "PERCENTUAL"
        ]
    ]
    .rename(
        columns={
            "DEV_TOTAL_FMT": "DEVOLUÇÃO",
            "VLVENDA_FMT": "VENDA",
            "PERCENTUAL": "% DEV"
        }
    )
    .head(10),
    use_container_width=True,
    hide_index=True
)

st.markdown("---")

    # ======================================
    # RANKING GERENTES
    # ======================================

st.subheader(
        "📊 RANKING GERENTES"
    )

gerentes_rank = (
        filtro.groupby("NOMEGERENTE")
        ["DEV_TOTAL"]
        .sum()
        .abs()
        .reset_index()
        .sort_values(
            "DEV_TOTAL",
            ascending=False
        )
    )

fig_ger = px.bar(
        gerentes_rank,
        x="NOMEGERENTE",
        y="DEV_TOTAL",
        color_discrete_sequence=[AZUL]
    )

fig_ger.update_layout(
        template="plotly_dark",
        paper_bgcolor=FUNDO,
        plot_bgcolor=FUNDO,
        height=450
    )

st.plotly_chart(
        fig_ger,
        use_container_width=True
    )

    # ======================================
    # RANKING SUPERVISORES
    # ======================================

st.subheader(
        "👔 RANKING SUPERVISORES"
    )

supervisores_rank = (
        filtro.groupby("SUPERVISOR")
        ["DEV_TOTAL"]
        .sum()
        .abs()
        .reset_index()
        .sort_values(
            "DEV_TOTAL",
            ascending=False
        )
    )

fig_sup = px.bar(
        supervisores_rank,
        x="SUPERVISOR",
        y="DEV_TOTAL",
        color_discrete_sequence=[AMARELO]
    )

fig_sup.update_layout(
        template="plotly_dark",
        paper_bgcolor=FUNDO,
        plot_bgcolor=FUNDO,
        height=450
    )

st.plotly_chart(
        fig_sup,
        use_container_width=True
    )

# ==========================================
# ABA 3 - BASE ANALÍTICA
# ==========================================

with aba3:

    st.subheader(
        "📋 BASE ANALÍTICA"
    )

    st.dataframe(
        filtro,
        use_container_width=True,
        height=700
    )

    csv = (
        filtro
        .to_csv(
            index=False,
            sep=";"
        )
        .encode("utf-8")
    )

    st.download_button(
        "⬇️ Exportar CSV",
        csv,
        "Analise_Devolucoes.csv",
        "text/csv"
    )

# ==========================================
# RODAPÉ
# ==========================================

st.markdown("---")

st.markdown(
    """
<div style='text-align:center;
            color:#A9B4C2;
            padding:15px'>

Dashboard de Devoluções • Distrinorte

Desenvolvido por Paulo Gusmão • T.I Distrinorte

</div>
""",
    unsafe_allow_html=True
)