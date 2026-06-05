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

# ==========================================
# CONFIGURAÇÃO
# ==========================================

st.set_page_config(
    page_title="Dashboard Devoluções - MAIO 2026",
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
# PLANILHA
# ==========================================

ARQUIVO = "dados/Analise_Conta_Corrente.xlsx"


@st.cache_data
def carregar():

    df = pd.read_excel(ARQUIVO)

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

    if "ACIMA_TABELA" not in df.columns:
        df["ACIMA_TABELA"] = 0

    if "DEV_GRANDES_REDES" not in df.columns:
        df["DEV_GRANDES_REDES"] = 0

    if "DEMAIS_DEV" not in df.columns:
        df["DEMAIS_DEV"] = 0

    if "TV11" not in df.columns:
        df["TV11"] = 0

    if "TV5" not in df.columns:
        df["TV5"] = 0

    df["DEV_TOTAL"] = (
        df["DEV_GRANDES_REDES"]
        + df["DEMAIS_DEV"]
    )

    df["IMPACTO_FINANCEIRO"] = (
    df["DEV_GRANDES_REDES"].abs()
    + df["DEMAIS_DEV"].abs()
    + df["TV11"].abs()
    + df["TV5"].abs()
)

    return df


df = carregar()

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

col1, col2 = st.columns([4, 1])

with col1:
    st.title(
        "📊 DASHBOARD DE DEVOLUÇÕES - MAIO 2026"
    )

with col2:

    try:
        logo = Image.open(
            "assets/Logo Distrinorte Branca.png"
        )

        st.image(
            logo,
            width=480
        )

    except:
        st.warning(
            "Logo não encontrada."
        )

# ==========================================
# INDICADORES
# ==========================================

vendas = abs(filtro["VLVENDA"].sum())

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

impacto = (
    vendas
    - dev_total
    - trocas
    - bonificacoes
    + acima_tabela
)

perc_dev = (
    (dev_total / vendas) * 100
    if vendas > 0
    else 0
)

# ==========================================
# CARDS
# ==========================================

# PRIMEIRA LINHA
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("💰 VENDAS FATURADAS - DEVOLUÇÕES (ROTINA 111)", moeda(vendas))

with c2:
    st.metric("↩️ DEVOLUÇÕES TOTAIS", moeda(dev_total))

with c3:
    st.metric("🏢 DEVOLUÇÕES - GRANDES REDES", moeda(grandes_redes))

with c4:
    st.metric("🔄 TROCAS TOTAIS (TV11)", moeda(trocas))


# SEGUNDA LINHA
c5, c6, c7, c8 = st.columns(4)

with c5:
    st.metric("🎁 BONIFICAÇÕES (TV5)", moeda(bonificacoes))

with c6:
    st.metric("📉 % DEVOLUÇÕES SOBRE A VENDA", percentual(perc_dev))

with c7:
    st.metric("📈 VENDIDO ACIMA DA TABELA", moeda(acima_tabela))

with c8:
    st.metric("⚠️ IMPACTO FINANCEIRO NEGATIVO", moeda(impacto))

# ==========================================
# ABAS
# ==========================================

aba1, aba2, aba3 = st.tabs(
    [
        "📊 RESUMO EXECUTIVO",
        "🏆 RANKINGS",
        "📋 BASE ANALÍTICA"
    ]
)
# ==========================================
# ABA 1 - RESUMO EXECUTIVO
# ==========================================

with aba1:

    col1, col2 = st.columns(2)

    # ======================================
    # DONUT
    # ======================================

    with col1:

        composicao = pd.DataFrame(
            {
                "Categoria": [
                    "Grandes Redes",
                    "Dev. Normais",
                    "Trocas",
                    "Bonificações",
                    "Acima da Tabela"
                ],
                "Valor": [
                    grandes_redes,
                    dev_normais,
                    trocas,
                    bonificacoes,
                    acima_tabela
                ]
            }
        )

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
                "Acima da Tabela": VERDE
            }
        )

        fig_donut.update_traces(
            textinfo="percent",
            textfont_size=14
        )

        fig_donut.update_layout(
            template="plotly_dark",
            paper_bgcolor=FUNDO,
            plot_bgcolor=FUNDO,
            font_color="white",
            title="Composição Financeira",
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
            filtro
            .groupby("RCA")["IMPACTO_FINANCEIRO"]
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
            title="Top 15 Impacto Financeiro",
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
            font_color="white",
            height=520,
            yaxis={
                "categoryorder": "total ascending"
            }
        )

        st.plotly_chart(
            fig_impacto,
            use_container_width=True
        )

    st.markdown("---")

    # ======================================
    # PARETO DE DEVOLUÇÕES
    # ======================================

    pareto = (
        filtro
        .groupby("RCA")["DEV_TOTAL"]
        .sum()
        .abs()
        .reset_index()
        .sort_values(
            "DEV_TOTAL",
            ascending=False
        )
    )

    pareto["ACUMULADO"] = (
        pareto["DEV_TOTAL"].cumsum()
    )

    pareto["PERC_ACUM"] = (
        pareto["ACUMULADO"]
        / pareto["DEV_TOTAL"].sum()
    ) * 100

    pareto["RCA_CURTO"] = (
        pareto["RCA"]
        .astype(str)
        .str[:25]
    )

    fig_pareto = go.Figure()

    fig_pareto.add_trace(
        go.Bar(
            x=pareto["RCA_CURTO"],
            y=pareto["DEV_TOTAL"],
            marker_color=AZUL,
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
        font_color="white",
        title="Pareto de Devoluções",
        height=550,
        yaxis=dict(
            title="Valor"
        ),
        yaxis2=dict(
            title="% Acumulado",
            overlaying="y",
            side="right",
            range=[0, 100]
        )
    )

    st.plotly_chart(
        fig_pareto,
        use_container_width=True
    )

    st.markdown("---")

    # ======================================
    # SCATTER
    # ======================================

    scatter = (
        filtro
        .groupby("RCA")
        .agg(
            {
                "VLVENDA": "sum",
                "IMPACTO_FINANCEIRO": "sum"
            }
        )
        .reset_index()
    )

    fig_scatter = px.scatter(
        scatter,
        x="VLVENDA",
        y="IMPACTO_FINANCEIRO",
        hover_name="RCA",
        title="Venda x Impacto Financeiro",
        color_discrete_sequence=[AMARELO]
    )

    fig_scatter.update_traces(
        marker=dict(
            size=12,
            line=dict(
                color=AZUL,
                width=2
            )
        )
    )

    fig_scatter.update_layout(
        template="plotly_dark",
        paper_bgcolor=FUNDO,
        plot_bgcolor=FUNDO,
        font_color="white",
        height=550
    )

    st.plotly_chart(
        fig_scatter,
        use_container_width=True
    )

# ==========================================
# ABA 2 - RANKINGS
# ==========================================

with aba2:

    st.selectbox(
        "Ordenação dos Rankings",
        ["% Sobre Venda"],
        disabled=False
    )

    def ranking_rca(campo, titulo):

        base = (
            filtro
            .groupby("RCA")
            .agg(
                {
                    campo: "sum",
                    "VLVENDA": "sum"
                }
            )
            .reset_index()
        )

        base[campo] = base[campo].abs()

        base["PERC_NUM"] = (
            base[campo]
            / base["VLVENDA"]
        ).fillna(0) * 100

        base = base.sort_values(
            "PERC_NUM",
            ascending=False
        )

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
            base.head(20),
            use_container_width=True,
            hide_index=True
        )

    col1, col2 = st.columns(2)

    with col1:

        ranking_rca(
            "DEV_GRANDES_REDES",
            "🏢 TOP 20 GRANDES REDES"
        )

        ranking_rca(
            "TV11",
            "🔄 TOP 20 TROCAS"
        )

    with col2:

        ranking_rca(
            "DEMAIS_DEV",
            "👥 TOP 20 DEVOLUÇÕES NORMAIS"
        )

        ranking_rca(
            "TV5",
            "🎁 TOP 20 BONIFICAÇÕES"
        )

    st.markdown("---")

    # ======================================
    # RANKING GERENTES
    # ======================================

    st.subheader("📊 RANKING - DEVOLUÇÃO DOS GERENTES")

    gerentes = (
        filtro
        .groupby("NOMEGERENTE")["DEV_TOTAL"]
        .sum()
        .abs()
        .reset_index()
    )

    fig_ger = px.bar(
        gerentes.sort_values(
            "DEV_TOTAL",
            ascending=False
        ),
        x="NOMEGERENTE",
        y="DEV_TOTAL",
        color_discrete_sequence=[AZUL]
    )

    fig_ger.update_layout(
        template="plotly_dark",
        paper_bgcolor=FUNDO,
        plot_bgcolor=FUNDO,
        font_color="white",
        height=450
    )

    st.plotly_chart(
        fig_ger,
        use_container_width=True
    )

    # ======================================
    # RANKING SUPERVISORES
    # ======================================

    st.subheader("👔 RANKING - DEVOLUÇÃO DOS SUPERVISORES")

    supervisores = (
        filtro
        .groupby("SUPERVISOR")["DEV_TOTAL"]
        .sum()
        .abs()
        .reset_index()
    )

    fig_sup = px.bar(
        supervisores.sort_values(
            "DEV_TOTAL",
            ascending=False
        ),
        x="SUPERVISOR",
        y="DEV_TOTAL",
        color_discrete_sequence=[AMARELO]
    )

    fig_sup.update_traces(
        marker_line_color=AZUL,
        marker_line_width=1.5
    )

    fig_sup.update_layout(
        template="plotly_dark",
        paper_bgcolor=FUNDO,
        plot_bgcolor=FUNDO,
        font_color="white",
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

    st.subheader("📋 Base Analítica")

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
<div style='text-align:center;color:#A9B4C2;padding:15px'>
Dashboard de Devoluções • Distrinorte • Maio/2026 - By Paulo Gusmão - T.I Distrinorte
</div>
""",
    unsafe_allow_html=True
)

#streamlit run app.py