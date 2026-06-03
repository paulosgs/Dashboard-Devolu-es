import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# CORES
# ==========================================

AZUL = "#00BFFF"
AMARELO = "#FDBE2D"
FUNDO = "#08111f"
CARD = "#111c2e"

# ==========================================
# CONFIGURAÇÃO
# ==========================================

st.set_page_config(
    page_title="Dashboard Devoluções",
    page_icon="📊",
    layout="wide"
)

# ==========================================
# CSS
# ==========================================

st.markdown(f"""
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
""", unsafe_allow_html=True)

# ==========================================
# LEITURA
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

    # ======================

    df["DEV_TOTAL"] = (
        df["DEV_GRANDES_REDES"]
        +
        df["DEMAIS_DEV"]
    )

    df["IMPACTO_FINANCEIRO"] = (
        df["DEV_GRANDES_REDES"]
        +
        df["DEMAIS_DEV"]
        +
        df["TV11"]
        +
        df["TV5"]
    )

    return df

df = carregar()

# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.title("Filtros")

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

st.title("📊 DASHBOARD DE DEVOLUÇÕES")

st.markdown(
    f"""
    <hr style="
        border:1px solid {AZUL};
        margin-top:10px;
        margin-bottom:20px;
    ">
    """,
    unsafe_allow_html=True
)

# ==========================================
# INDICADORES
# ==========================================

vendas = filtro["VLVENDA"].sum()

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

impacto = abs(
    filtro["IMPACTO_FINANCEIRO"].sum()
)

perc_dev = (
    (dev_total / vendas) * 100
    if vendas > 0
    else 0
)

# ==========================================
# CARDS
# ==========================================

c1,c2,c3,c4,c5,c6 = st.columns(6)

with c1:
    st.metric(
        "VENDAS",
        f"R$ {vendas:,.0f}"
    )

with c2:
    st.metric(
        "DEVOLUÇÕES",
        f"R$ {dev_total:,.0f}"
    )

with c3:
    st.metric(
        "GRANDES REDES",
        f"R$ {grandes_redes:,.0f}"
    )

with c4:
    st.metric(
        "TROCAS",
        f"R$ {trocas:,.0f}"
    )

with c5:
    st.metric(
        "BONIFICAÇÕES",
        f"R$ {bonificacoes:,.0f}"
    )

with c6:
    st.metric(
        "% DEV",
        f"{perc_dev:.2f}%"
    )

# ==========================================
# ABAS
# ==========================================

aba1, aba2, aba3 = st.tabs(
    [
        "📊 Resumo Executivo",
        "🏆 Rankings",
        "📋 Base Analítica"
    ]
)

# ==========================================
# RESUMO EXECUTIVO
# ==========================================

with aba1:

    col1, col2 = st.columns(2)

    # ==================================
    # DONUT
    # ==================================

    with col1:

        composicao = pd.DataFrame({
            "Categoria":[
                "Grandes Redes",
                "Dev. Normais",
                "Trocas",
                "Bonificações"
            ],
            "Valor":[
                grandes_redes,
                dev_normais,
                trocas,
                bonificacoes
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
                "Bonificações": "#FFE082"
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
            height=520,
            legend=dict(
                orientation="h",
                y=-0.2
            ),
            title="Composição Financeira"
        )

        st.plotly_chart(
            fig_donut,
            use_container_width=True
        )

    # ==================================
    # TOP IMPACTO
    # ==================================

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
            title="Top 15 Impacto Financeiro",
            color_discrete_sequence=[
                AMARELO
            ]
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
                "categoryorder":
                "total ascending"
            }
        )

        st.plotly_chart(
            fig_impacto,
            use_container_width=True
        )

    st.markdown("---")
    # ==========================================
    # PARETO DE DEVOLUÇÕES
    # ==========================================

    pareto = (
        filtro.groupby("RCA")["DEV_TOTAL"]
        .sum()
        .abs()
        .reset_index()
        .sort_values(
            "DEV_TOTAL",
            ascending=False
        )
    )

    pareto["ACUMULADO"] = pareto["DEV_TOTAL"].cumsum()

    pareto["PERC_ACUM"] = (
        pareto["ACUMULADO"]
        /
        pareto["DEV_TOTAL"].sum()
    ) * 100

    pareto["RCA_CURTO"] = (
        pareto["RCA"]
        .astype(str)
        .str[:30]
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
            line=dict(
                color=AMARELO,
                width=3
            ),
            yaxis="y2",
            name="% Acumulado"
        )
    )

    fig_pareto.update_layout(
        title="Pareto de Devoluções",
        template="plotly_dark",
        paper_bgcolor=FUNDO,
        plot_bgcolor=FUNDO,
        height=500,
        yaxis=dict(title="Valor"),
        yaxis2=dict(
            title="% Acumulado",
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

    # ==========================================
    # SCATTER
    # ==========================================

    scatter = (
        filtro.groupby("RCA")
        .agg({
            "VLVENDA":"sum",
            "IMPACTO_FINANCEIRO":"sum"
        })
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
        height=550
    )

    st.plotly_chart(
        fig_scatter,
        use_container_width=True
    )

# ==========================================
# ABA RANKINGS
# ==========================================

with aba2:

    def ranking_rca(campo, titulo):

        base = (
            filtro.groupby("RCA")
            .agg({
                campo:"sum",
                "VLVENDA":"sum"
            })
            .reset_index()
        )

        base[campo] = base[campo].abs()

        base["% SOBRE VENDA"] = (
            base[campo]
            /
            base["VLVENDA"]
        ).fillna(0) * 100

        base = base.sort_values(
            campo,
            ascending=False
        )

        st.subheader(titulo)

        st.dataframe(
            base.head(20),
            use_container_width=True,
            hide_index=True
        )

    col_rank1,col_rank2 = st.columns(2)

    with col_rank1:

        ranking_rca(
            "DEV_GRANDES_REDES",
            "🏢 Top 20 Grandes Redes"
        )

        ranking_rca(
            "TV11",
            "🔄 Top 20 Trocas"
        )

    with col_rank2:

        ranking_rca(
            "DEMAIS_DEV",
            "👥 Top 20 Devoluções Normais"
        )

        ranking_rca(
            "TV5",
            "🎁 Top 20 Bonificações"
        )

    st.markdown("---")

    # ==========================================
    # GERENTES
    # ==========================================

    st.subheader("📊 Ranking Gerentes")

    gerentes = (
        filtro.groupby("NOMEGERENTE")
        .agg({
            "DEV_TOTAL":"sum",
            "VLVENDA":"sum"
        })
        .reset_index()
    )

    gerentes["DEV_TOTAL"] = (
        gerentes["DEV_TOTAL"]
        .abs()
    )

    gerentes["% SOBRE VENDA"] = (
        gerentes["DEV_TOTAL"]
        /
        gerentes["VLVENDA"]
    ) * 100

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
        height=450
    )

    st.plotly_chart(
        fig_ger,
        use_container_width=True
    )

    # ==========================================
    # SUPERVISORES
    # ==========================================

    st.subheader("👔 Ranking Supervisores")

    supervisores = (
        filtro.groupby("SUPERVISOR")
        .agg({
            "DEV_TOTAL":"sum",
            "VLVENDA":"sum"
        })
        .reset_index()
    )

    supervisores["DEV_TOTAL"] = (
        supervisores["DEV_TOTAL"]
        .abs()
    )

    supervisores["% SOBRE VENDA"] = (
        supervisores["DEV_TOTAL"]
        /
        supervisores["VLVENDA"]
    ) * 100

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
        height=450
    )

    st.plotly_chart(
        fig_sup,
        use_container_width=True
    )

# ==========================================
# ABA ANALÍTICA
# ==========================================

with aba3:

    st.subheader("📋 Base Analítica")

    base_analitica = filtro[
        [
            "NOMEGERENTE",
            "SUPERVISOR",
            "RCA",
            "VLVENDA",
            "DEV_GRANDES_REDES",
            "DEMAIS_DEV",
            "TV11",
            "TV5",
            "DEV_TOTAL",
            "IMPACTO_FINANCEIRO",
            "CONTA_CORRENTE"
        ]
    ]

    st.dataframe(
        base_analitica,
        use_container_width=True,
        height=650
    )

    csv = base_analitica.to_csv(
        index=False,
        sep=";"
    ).encode("utf-8")

    st.download_button(
        "⬇️ Exportar CSV",
        csv,
        "Analise_Devolucoes.csv",
        "text/csv"
    )

# ==========================================
# RODAPÉ
# ==========================================

st.markdown(
    f"""
    <hr style='border:1px solid {AZUL};'>
    <center>
        <span style='color:#999999'>
            Dashboard de Devoluções • Distrinorte
        </span>
    </center>
    """,
    unsafe_allow_html=True
)