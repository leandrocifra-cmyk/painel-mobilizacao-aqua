import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import date, datetime, timedelta

# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="Mobilização | Aqua Pernambuco – Enorsul",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# === BLACK PIANO V0 ===
st.markdown("""
<style>

/* =========================================================
   BLACK PIANO — ENORSUL
   Fundo preto | Cards grafite | Texto branco | Destaque vermelho
   ========================================================= */

/* CANVAS PRINCIPAL */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.stApp,
.main {
    background: #050506 !important;
    color: #F5F5F7 !important;
}

[data-testid="stMainBlockContainer"],
.block-container {
    background: #050506 !important;
}

/* HEADER */
[data-testid="stHeader"] {
    background: rgba(5,5,6,0.96) !important;
}

/* SIDEBAR */
[data-testid="stSidebar"],
[data-testid="stSidebarContent"] {
    background: #09090B !important;
    border-right: 1px solid #242429 !important;
}

/* TEXTO */
h1, h2, h3, h4, h5, h6,
p, span, label,
[data-testid="stMarkdownContainer"],
[data-testid="stCaptionContainer"] {
    color: #F5F5F7;
}

/* MÉTRICAS */
[data-testid="stMetric"] {
    background: #101014 !important;
    border: 1px solid #26262C !important;
    border-radius: 14px !important;
    padding: 16px 18px !important;
    box-shadow: 0 8px 24px rgba(0,0,0,.28) !important;
}

[data-testid="stMetricLabel"] * {
    color: #A8A8B0 !important;
}

[data-testid="stMetricValue"] {
    color: #FFFFFF !important;
}

[data-testid="stMetricDelta"] * {
    color: #D7D7DC !important;
}

/* CONTAINERS / CARDS */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: #0D0D10 !important;
    border: 1px solid #242429 !important;
    border-radius: 14px !important;
}

/* TABS */
[data-testid="stTabs"] {
    background: transparent !important;
}

button[data-baseweb="tab"] {
    color: #B9B9C0 !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #FFFFFF !important;
    border-bottom-color: #E31B2D !important;
}

/* INPUTS */
[data-baseweb="input"] > div,
[data-baseweb="select"] > div,
[data-baseweb="textarea"] {
    background: #111115 !important;
    color: #FFFFFF !important;
    border-color: #303036 !important;
}

input, textarea {
    color: #FFFFFF !important;
    background: #111115 !important;
}

/* BOTÕES */
.stButton > button,
.stFormSubmitButton > button {
    background: #17171C !important;
    color: #FFFFFF !important;
    border: 1px solid #35353C !important;
    border-radius: 9px !important;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    border-color: #E31B2D !important;
    color: #FFFFFF !important;
}

/* BOTÃO PRIMÁRIO */
button[kind="primary"] {
    background: #E31B2D !important;
    border-color: #E31B2D !important;
    color: #FFFFFF !important;
}

/* DATAFRAMES / TABELAS */
[data-testid="stDataFrame"],
[data-testid="stTable"] {
    background: #0D0D10 !important;
    border-radius: 12px !important;
}

/* EXPANDERS */
[data-testid="stExpander"] {
    background: #0D0D10 !important;
    border: 1px solid #242429 !important;
    border-radius: 12px !important;
}

/* ALERTAS */
[data-testid="stAlert"] {
    border-radius: 10px !important;
}

/* DIVISORES */
hr {
    border-color: #25252A !important;
}

/* LINKS */
a {
    color: #F05A67 !important;
}

/* REMOVE FUNDOS CLAROS DE ELEMENTOS EMBUTIDOS */
iframe {
    background: transparent !important;
}

/* SCROLLBAR */
::-webkit-scrollbar {
    width: 10px;
    height: 10px;
}

::-webkit-scrollbar-track {
    background: #050506;
}

::-webkit-scrollbar-thumb {
    background: #303036;
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: #E31B2D;
}

</style>
""", unsafe_allow_html=True)


API_URL = "https://aqua-mobilizacao-api.leandro-cifra.workers.dev"
GO_LIVE = date(2026, 10, 26)

STATUS_VALIDOS = [
    "Não iniciado",
    "Em andamento",
    "Aguardando Aqua",
    "Concluído",
    "Cancelado",
]

ORDEM_PRIORIDADE = {
    "Crítica": 1,
    "Alta": 2,
    "Média": 3,
    "Baixa": 4,
}

# ============================================================
# ESTILO
# ============================================================

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.4rem;
            padding-bottom: 3rem;
            max-width: 1600px;
        }

        [data-testid="stSidebar"] {
            border-right: 1px solid #E5E7EB;
        }

        h1 {
            font-size: 2rem !important;
            font-weight: 750 !important;
            letter-spacing: -0.03em;
        }

        h2 {
            font-size: 1.35rem !important;
            font-weight: 700 !important;
            margin-top: 1.2rem !important;
        }

        h3 {
            font-size: 1.05rem !important;
            font-weight: 700 !important;
        }

        [data-testid="stMetric"] {
            background: white;
            border: 1px solid #E5E7EB;
            border-radius: 12px;
            padding: 14px 16px;
            min-height: 105px;
        }

        [data-testid="stMetricLabel"] {
            font-weight: 600;
        }

        [data-testid="stMetricValue"] {
            font-weight: 750;
        }

        .titulo-pagina {
            margin-bottom: 0.1rem;
        }

        .subtitulo {
            color: #667085;
            font-size: 0.93rem;
            margin-bottom: 1.25rem;
        }

        .card {
            background: white;
            border: 1px solid #E5E7EB;
            border-radius: 12px;
            padding: 16px 18px;
            margin-bottom: 12px;
        }

        .card-titulo {
            font-weight: 700;
            font-size: 0.96rem;
            margin-bottom: 6px;
        }

        .card-texto {
            color: #475467;
            font-size: 0.90rem;
            line-height: 1.45;
        }

        .tag {
            display: inline-block;
            border-radius: 999px;
            padding: 4px 9px;
            font-size: 0.76rem;
            font-weight: 650;
            background: #F2F4F7;
            margin-right: 5px;
            margin-bottom: 5px;
        }

        .rodape {
            color: #98A2B3;
            font-size: 0.78rem;
            margin-top: 2.5rem;
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid #EAECF0;
            border-radius: 10px;
        }

        .modo-reuniao {
            padding: 6px 0 12px 0;
            color: #667085;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# API
# ============================================================

@st.cache_data(ttl=60, show_spinner=False)
def carregar_api(rota):
    resposta = requests.get(f"{API_URL}/{rota}", timeout=20)
    resposta.raise_for_status()
    return resposta.json()


def salvar_api(rota, payload):
    resposta = requests.put(f"{API_URL}/{rota}", json=payload, timeout=30)
    if not resposta.ok:
        try:
            detalhe = resposta.json()
        except Exception:
            detalhe = resposta.text
        raise RuntimeError(f"Erro {resposta.status_code}: {detalhe}")
    return resposta.json()


def limpar_recarregar():
    st.cache_data.clear()
    st.rerun()


def carregar_dados():
    rotas = [
        "resumo",
        "atividades",
        "frentes",
        "polos",
        "pessoas",
        "recursos",
        "rampagem",
    ]

    dados = {}

    for rota in rotas:
        try:
            dados[rota] = carregar_api(rota)
        except Exception:
            dados[rota] = []

    return dados


dados = carregar_dados()

df_resumo = pd.DataFrame(dados["resumo"])
df_atividades = pd.DataFrame(dados["atividades"])
df_frentes = pd.DataFrame(dados["frentes"])
df_polos = pd.DataFrame(dados["polos"])
df_pessoas = pd.DataFrame(dados["pessoas"])
df_recursos = pd.DataFrame(dados["recursos"])
df_rampagem = pd.DataFrame(dados["rampagem"])

# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def numero(valor):
    try:
        if pd.isna(valor):
            return 0
        return int(valor)
    except Exception:
        return 0


def texto(valor, padrao="—"):
    if valor is None:
        return padrao
    try:
        if pd.isna(valor):
            return padrao
    except Exception:
        pass

    valor = str(valor).strip()

    if not valor or valor.lower() in ["none", "nan", "nat"]:
        return padrao

    return valor


def converter_data(valor):
    if valor is None:
        return None

    try:
        if pd.isna(valor):
            return None
    except Exception:
        pass

    try:
        return pd.to_datetime(valor).date()
    except Exception:
        return None


def data_br(valor):
    d = converter_data(valor)
    return d.strftime("%d/%m/%Y") if d else "—"


def percentual_mobilizacao(total, concluidos, cancelados=0):
    validos = max(numero(total) - numero(cancelados), 0)

    if validos == 0:
        return 0.0

    return numero(concluidos) / validos * 100


def coluna_existente(df, coluna, valor_padrao=None):
    if coluna not in df.columns:
        df[coluna] = valor_padrao
    return df


def preparar_atividades(df):
    if df.empty:
        return df

    df = df.copy()

    campos = [
        "id",
        "frente",
        "macroetapa",
        "atividade",
        "prioridade",
        "status",
        "percentual",
        "responsavel",
        "data_inicio",
        "data_prevista",
        "data_conclusao",
        "pendencia_acao",
        "prazo_pendencia",
        "proximo_passo_manual",
        "observacao",
        "evidencia",
        "criterio_aceite",
        "dependencia",
        "polo_base",
    ]

    for campo in campos:
        if campo not in df.columns:
            df[campo] = None

    df["data_prevista_dt"] = pd.to_datetime(
        df["data_prevista"], errors="coerce"
    )

    df["prazo_pendencia_dt"] = pd.to_datetime(
        df["prazo_pendencia"], errors="coerce"
    )

    df["ordem_prioridade"] = (
        df["prioridade"].map(ORDEM_PRIORIDADE).fillna(99)
    )

    hoje = pd.Timestamp(date.today())

    df["atrasada"] = (
        df["data_prevista_dt"].notna()
        & (df["data_prevista_dt"] < hoje)
        & (~df["status"].isin(["Concluído", "Cancelado"]))
    )

    df["prazo_proximo"] = (
        df["data_prevista_dt"].notna()
        & (df["data_prevista_dt"] >= hoje)
        & (df["data_prevista_dt"] <= hoje + pd.Timedelta(days=7))
        & (~df["status"].isin(["Concluído", "Cancelado"]))
    )

    return df


df_atividades = preparar_atividades(df_atividades)


def totais_gerais():
    if df_resumo.empty:
        return {
            "total": 0,
            "concluidos": 0,
            "em_andamento": 0,
            "aguardando_aqua": 0,
            "nao_iniciados": 0,
            "cancelados": 0,
            "percentual": 0,
        }

    campos = [
        "total",
        "concluidos",
        "em_andamento",
        "aguardando_aqua",
        "nao_iniciados",
        "cancelados",
    ]

    totais = {}

    for campo in campos:
        if campo in df_resumo.columns:
            totais[campo] = int(
                pd.to_numeric(
                    df_resumo[campo], errors="coerce"
                ).fillna(0).sum()
            )
        else:
            totais[campo] = 0

    totais["percentual"] = percentual_mobilizacao(
        totais["total"],
        totais["concluidos"],
        totais["cancelados"],
    )

    return totais


totais = totais_gerais()


def proximo_passo(row):
    manual = texto(row.get("proximo_passo_manual"), "")

    if manual:
        return manual

    pendencia = texto(row.get("pendencia_acao"), "")

    if pendencia:
        return pendencia

    return "—"


def pontos_criticos(df, limite=10):
    if df.empty:
        return df

    base = df[
        ~df["status"].isin(["Concluído", "Cancelado"])
    ].copy()

    if base.empty:
        return base

    def nivel(row):
        if bool(row.get("atrasada")):
            return 1
        if row.get("status") == "Aguardando Aqua":
            return 2
        if bool(row.get("prazo_proximo")):
            return 3
        if row.get("prioridade") == "Crítica":
            return 4
        if row.get("prioridade") == "Alta":
            return 5
        return 6

    base["nivel_critico"] = base.apply(nivel, axis=1)

    base = base.sort_values(
        ["nivel_critico", "ordem_prioridade", "data_prevista_dt"],
        na_position="last",
    )

    return base.head(limite)


def tabela_atividades(df):
    if df.empty:
        st.info("Nenhuma atividade cadastrada para esta seleção.")
        return

    exibicao = df.copy()

    exibicao["Prazo"] = exibicao["data_prevista"].apply(data_br)
    exibicao["Próximo passo"] = exibicao.apply(proximo_passo, axis=1)

    colunas = [
        "macroetapa",
        "atividade",
        "polo_base",
        "prioridade",
        "status",
        "percentual",
        "responsavel",
        "Prazo",
        "dependencia",
        "Próximo passo",
    ]

    colunas = [c for c in colunas if c in exibicao.columns]

    exibicao = exibicao[colunas]

    nomes = {
        "macroetapa": "Macroetapa",
        "atividade": "Atividade",
        "polo_base": "Polo/Base",
        "prioridade": "Prioridade",
        "status": "Status",
        "percentual": "%",
        "responsavel": "Responsável",
        "dependencia": "Dependência",
    }

    exibicao = exibicao.rename(columns=nomes)

    st.dataframe(
        exibicao,
        use_container_width=True,
        hide_index=True,
        height=520,
    )


def cabecalho(titulo, subtitulo=None):
    st.markdown(
        f"<h1 class='titulo-pagina'>{titulo}</h1>",
        unsafe_allow_html=True,
    )

    if subtitulo:
        st.markdown(
            f"<div class='subtitulo'>{subtitulo}</div>",
            unsafe_allow_html=True,
        )


def indicadores_frente(nome_frente):
    if df_resumo.empty or "frente" not in df_resumo.columns:
        return

    linha = df_resumo[df_resumo["frente"] == nome_frente]

    if linha.empty:
        return

    linha = linha.iloc[0]

    total = numero(linha.get("total"))
    concluidos = numero(linha.get("concluidos"))
    andamento = numero(linha.get("em_andamento"))
    aqua = numero(linha.get("aguardando_aqua"))
    nao_iniciado = numero(linha.get("nao_iniciados"))
    cancelados = numero(linha.get("cancelados"))

    pct = percentual_mobilizacao(total, concluidos, cancelados)

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("Mobilização", f"{pct:.1f}%")
    c2.metric("Concluídos", concluidos)
    c3.metric("Em andamento", andamento)
    c4.metric("Aguardando Aqua", aqua)
    c5.metric("Não iniciados", nao_iniciado)


def grafico_macroetapas(base, chave):
    if base.empty or "macroetapa" not in base.columns:
        st.info("Sem dados de macroetapa.")
        return
    b = base[~base["status"].isin(["Cancelado"])].copy()
    b["macroetapa"] = b["macroetapa"].fillna("Sem macroetapa")
    macros = sorted(b["macroetapa"].astype(str).unique().tolist())
    if not macros:
        return
    for i in range(0, len(macros), 2):
        cols = st.columns(2)
        for j, macro in enumerate(macros[i:i+2]):
            d = b[b["macroetapa"].astype(str) == macro]
            cont = d["status"].value_counts().reindex(STATUS_VALIDOS[:-1], fill_value=0).reset_index()
            cont.columns = ["Status", "Quantidade"]
            cont = cont[cont["Quantidade"] > 0]
            with cols[j]:
                st.markdown(f"**{macro}**")
                fig = px.pie(cont, names="Status", values="Quantidade", hole=.62)
                fig.update_layout(height=290, margin=dict(l=5,r=5,t=10,b=5), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#F5F5F7", legend_title_text="")
                fig.update_traces(textposition="inside", textinfo="value")
                st.plotly_chart(fig, use_container_width=True, key=f"macro_{chave}_{i}_{j}")
                abertos = int((~d["status"].isin(["Concluído","Cancelado"])).sum())
                st.caption(f"{len(d)} atividades · {abertos} em aberto")


def editor_atividade(base, nome_frente):
    if base.empty:
        st.info("Nenhuma atividade disponível para atualização.")
        return
    opcoes = {}
    for _, r in base.sort_values(["macroetapa","id"], na_position="last").iterrows():
        label = f"{numero(r.get('id'))} — {texto(r.get('macroetapa'))} — {texto(r.get('atividade'))}"
        opcoes[label] = r
    escolha = st.selectbox("Atividade", list(opcoes), key=f"edit_atividade_{nome_frente}")
    r = opcoes[escolha]
    status_atual = texto(r.get("status"), "Não iniciado")
    prioridade_atual = texto(r.get("prioridade"), "Média")
    prioridades = ["Crítica","Alta","Média","Baixa"]
    if prioridade_atual not in prioridades: prioridade_atual="Média"
    with st.form(f"form_atividade_{nome_frente}_{numero(r.get('id'))}"):
        c1,c2,c3=st.columns(3)
        status=c1.selectbox("Status", STATUS_VALIDOS, index=STATUS_VALIDOS.index(status_atual) if status_atual in STATUS_VALIDOS else 0)
        prioridade=c2.selectbox("Prioridade", prioridades, index=prioridades.index(prioridade_atual))
        percentual=c3.number_input("Percentual",0,100,numero(r.get("percentual")),1)
        responsavel=st.text_input("Responsável", value=texto(r.get("responsavel"),""))
        d1,d2,d3=st.columns(3)
        inicio=d1.date_input("Data de início", value=converter_data(r.get("data_inicio")))
        prevista=d2.date_input("Data prevista", value=converter_data(r.get("data_prevista")))
        conclusao=d3.date_input("Data de conclusão", value=converter_data(r.get("data_conclusao")))
        dependencia=st.text_area("Dependência", value=texto(r.get("dependencia"),""))
        pendencia=st.text_area("Pendência / Ação", value=texto(r.get("pendencia_acao"),""))
        proximo=st.text_area("Próximo passo manual", value=texto(r.get("proximo_passo_manual"),""))
        criterio=st.text_area("Critério de aceite", value=texto(r.get("criterio_aceite"),""))
        evidencia=st.text_area("Evidência", value=texto(r.get("evidencia"),""))
        observacao=st.text_area("Observação", value=texto(r.get("observacao"),""))
        salvar=st.form_submit_button("Salvar alterações", use_container_width=True)
    if salvar:
        payload={"status":status,"prioridade":prioridade,"percentual":int(percentual),"responsavel":responsavel or None,"data_inicio":inicio.isoformat() if inicio else None,"data_prevista":prevista.isoformat() if prevista else None,"data_conclusao":conclusao.isoformat() if conclusao else None,"dependencia":dependencia or None,"pendencia_acao":pendencia or None,"proximo_passo_manual":proximo or None,"criterio_aceite":criterio or None,"evidencia":evidencia or None,"observacao":observacao or None,"atualizado_por":"Painel Mobilização"}
        try:
            salvar_api(f"atividades/{numero(r.get('id'))}",payload)
            st.success("Atividade atualizada no D1 e registrada no histórico.")
            limpar_recarregar()
        except Exception as e: st.error(f"Não foi possível salvar: {e}")

def pagina_frente(nome_frente):
    cabecalho(nome_frente, f"Acompanhamento da mobilização da frente de {nome_frente.lower()}.")
    indicadores_frente(nome_frente)
    if df_atividades.empty:
        st.info("Não há atividades disponíveis."); return
    base=df_atividades[df_atividades["frente"]==nome_frente].copy()
    tab_visao,tab_ativ,tab_atualizar=st.tabs(["Visão da frente","Atividades","Atualizar"])
    with tab_visao:
        st.markdown("## Pontos de atenção")
        criticos=pontos_criticos(base,6)
        if criticos.empty: st.success("Nenhum ponto crítico identificado nesta frente.")
        else:
            for _,row in criticos.iterrows():
                st.markdown(f"**{texto(row.get('atividade'))}** · {texto(row.get('status'))} · {texto(row.get('prioridade'))}  \nResponsável: {texto(row.get('responsavel'))} · Prazo: {data_br(row.get('data_prevista'))}")
        st.markdown("## Análise por macroetapa")
        grafico_macroetapas(base,f"frente_{nome_frente}")
    with tab_ativ:
        macroetapas=sorted([x for x in base["macroetapa"].dropna().unique().tolist() if str(x).strip()])
        f1,f2,f3=st.columns(3)
        macro=f1.selectbox("Macroetapa",["Todas"]+macroetapas,key=f"macro_filtro_{nome_frente}")
        status=f2.selectbox("Status",["Todos"]+STATUS_VALIDOS,key=f"status_filtro_{nome_frente}")
        prioridade=f3.selectbox("Prioridade",["Todas","Crítica","Alta","Média","Baixa"],key=f"prior_filtro_{nome_frente}")
        filtrado=base.copy()
        if macro!="Todas": filtrado=filtrado[filtrado["macroetapa"]==macro]
        if status!="Todos": filtrado=filtrado[filtrado["status"]==status]
        if prioridade!="Todas": filtrado=filtrado[filtrado["prioridade"]==prioridade]
        tabela_atividades(filtrado)
    with tab_atualizar:
        st.caption("As alterações são gravadas no D1 pelo Worker e registradas no histórico.")
        editor_atividade(base,nome_frente)


# ============================================================
# NAVEGAÇÃO
# ============================================================

with st.sidebar:
    st.markdown("## Mobilização")
    st.caption("Aqua Pernambuco · Enorsul")

    pagina = st.radio(
        "Navegação",
        [
            "Visão Geral",
            "Leitura",
            "Cobrança",
            "Hidrometria",
            "Pessoas & Estrutura",
            "Cronograma & Rampagem",
            "Modo Reunião",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    dias = (GO_LIVE - date.today()).days

    st.metric("Go-Live", "26/10/2026")
    st.caption(f"{dias} dias para o início operacional")

    if st.button("Atualizar dados", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ============================================================
# 1. VISÃO GERAL
# ============================================================

if pagina == "Visão Geral":
    cabecalho(
        "Mobilização | Aqua Pernambuco – Enorsul",
        "Visão executiva consolidada da implantação dos contratos.",
    )

    dias = (GO_LIVE - date.today()).days

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    c1.metric("Dias para Go-Live", dias)
    c2.metric("% Mobilização", f"{totais['percentual']:.1f}%")
    c3.metric("Concluídos", totais["concluidos"])
    c4.metric("Em andamento", totais["em_andamento"])
    c5.metric("Aguardando Aqua", totais["aguardando_aqua"])
    c6.metric("Não iniciados", totais["nao_iniciados"])

    st.markdown("## Análise por macroetapa")
    filtro_macro = st.selectbox("Visão", ["Geral", "Leitura", "Cobrança", "Hidrometria"], key="macro_geral_filtro")
    base_macro = df_atividades.copy()
    if filtro_macro != "Geral" and not base_macro.empty:
        base_macro = base_macro[base_macro["frente"] == filtro_macro]
    grafico_macroetapas(base_macro, f"geral_{filtro_macro}")

    st.markdown("## Mobilização por frente")

    if df_resumo.empty:
        st.warning("Resumo das frentes indisponível.")
    else:
        tabela = df_resumo.copy()

        tabela["% Mobilização"] = tabela.apply(
            lambda x: percentual_mobilizacao(
                x.get("total"),
                x.get("concluidos"),
                x.get("cancelados"),
            ),
            axis=1,
        )

        tabela["% Mobilização"] = tabela["% Mobilização"].map(
            lambda x: f"{x:.1f}%"
        )

        mapa = {
            "frente": "Frente",
            "total": "Total",
            "concluidos": "Concluído",
            "em_andamento": "Em andamento",
            "aguardando_aqua": "Aguardando Aqua",
            "nao_iniciados": "Não iniciado",
            "cancelados": "Cancelado",
        }

        colunas = [
            "frente",
            "total",
            "concluidos",
            "em_andamento",
            "aguardando_aqua",
            "nao_iniciados",
            "% Mobilização",
        ]

        colunas = [c for c in colunas if c in tabela.columns]

        tabela = tabela[colunas].rename(columns=mapa)

        st.dataframe(
            tabela,
            use_container_width=True,
            hide_index=True,
        )

    esquerda, direita = st.columns([1.15, 1])

    with esquerda:
        st.markdown("## Pontos críticos")

        criticos = pontos_criticos(df_atividades, 8)

        if criticos.empty:
            st.success("Nenhum ponto crítico identificado.")
        else:
            for _, row in criticos.iterrows():
                frente = texto(row.get("frente"))
                atividade = texto(row.get("atividade"))
                status = texto(row.get("status"))
                prioridade = texto(row.get("prioridade"))
                prazo = data_br(row.get("data_prevista"))

                st.markdown(
                    f"""
                    <div class="card">
                        <div class="card-titulo">{atividade}</div>
                        <div class="card-texto">
                            <b>{frente}</b> · {status} · {prioridade}<br>
                            Prazo: {prazo}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with direita:
        st.markdown("## Próximos passos")

        if df_atividades.empty:
            st.info("Nenhum próximo passo disponível.")
        else:
            proximos = df_atividades[
                ~df_atividades["status"].isin(
                    ["Concluído", "Cancelado"]
                )
            ].copy()

            proximos["proximo"] = proximos.apply(
                proximo_passo, axis=1
            )

            proximos = proximos[
                proximos["proximo"] != "—"
            ].copy()

            proximos = proximos.sort_values(
                ["ordem_prioridade", "data_prevista_dt"],
                na_position="last",
            ).head(8)

            if proximos.empty:
                st.info(
                    "Não há próximos passos registrados na base."
                )
            else:
                for _, row in proximos.iterrows():
                    st.markdown(
                        f"""
                        <div class="card">
                            <div class="card-titulo">
                                {texto(row.get("atividade"))}
                            </div>
                            <div class="card-texto">
                                {proximo_passo(row)}<br>
                                <b>Responsável:</b>
                                {texto(row.get("responsavel"))}
                                &nbsp; · &nbsp;
                                <b>Prazo:</b>
                                {data_br(row.get("data_prevista"))}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

# ============================================================
# 2, 3 e 4. FRENTES
# ============================================================

elif pagina == "Leitura":
    pagina_frente("Leitura")

elif pagina == "Cobrança":
    pagina_frente("Cobrança")

elif pagina == "Hidrometria":
    pagina_frente("Hidrometria")

# ============================================================
# 5. PESSOAS & ESTRUTURA
# ============================================================

elif pagina == "Pessoas & Estrutura":
    cabecalho(
        "Pessoas & Estrutura",
        "Visão interna da mobilização de pessoas, bases e recursos.",
    )

    total_pessoas = len(df_pessoas)

    def soma_flag(campo):
        if df_pessoas.empty or campo not in df_pessoas.columns:
            return 0

        return int(
            pd.to_numeric(
                df_pessoas[campo], errors="coerce"
            ).fillna(0).sum()
        )

    doc = soma_flag("documentacao_enviada")
    aprovados = soma_flag("aprovado_aqua")
    integrados = soma_flag("integrado")
    campo = soma_flag("liberado_campo")

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("Pessoas cadastradas", total_pessoas)
    c2.metric("Documentação enviada", doc)
    c3.metric("Aprovados Aqua", aprovados)
    c4.metric("Integrados", integrados)
    c5.metric("Liberados para campo", campo)

    st.markdown("## Funil de mobilização")

    funil = pd.DataFrame(
        {
            "Etapa": [
                "Pessoas cadastradas",
                "Documentação enviada",
                "Aprovados Aqua",
                "Integrados",
                "Liberados para campo",
            ],
            "Quantidade": [
                total_pessoas,
                doc,
                aprovados,
                integrados,
                campo,
            ],
        }
    )

    st.bar_chart(
        funil.set_index("Etapa"),
        horizontal=True,
    )

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Pessoas", "Polos e Bases", "Recursos", "Atualizar"]
    )

    with tab1:
        st.caption(
            "Base nominal de uso interno. Não é exibida no Modo Reunião."
        )

        if df_pessoas.empty:
            st.info("Nenhuma pessoa cadastrada.")
        else:
            pessoas = df_pessoas.copy()

            colunas = [
                "nome",
                "frente",
                "polo_base",
                "funcao",
                "situacao",
                "documentacao_enviada",
                "aprovado_aqua",
                "integrado",
                "liberado_campo",
                "data_admissao",
                "observacao",
            ]

            colunas = [
                c for c in colunas if c in pessoas.columns
            ]

            pessoas = pessoas[colunas].rename(
                columns={
                    "nome": "Nome",
                    "frente": "Frente",
                    "polo_base": "Polo/Base",
                    "funcao": "Função",
                    "situacao": "Situação",
                    "documentacao_enviada": "Documentação enviada",
                    "aprovado_aqua": "Aprovado Aqua",
                    "integrado": "Integrado",
                    "liberado_campo": "Liberado para campo",
                    "data_admissao": "Admissão",
                    "observacao": "Observação",
                }
            )

            st.dataframe(
                pessoas,
                use_container_width=True,
                hide_index=True,
                height=460,
            )

    with tab2:
        if df_polos.empty:
            st.info("Nenhum polo/base cadastrado.")
        else:
            polos = df_polos.copy()

            colunas = [
                "nome",
                "tipo",
                "regiao",
                "municipio_referencia",
                "observacao",
            ]

            colunas = [
                c for c in colunas if c in polos.columns
            ]

            polos = polos[colunas].rename(
                columns={
                    "nome": "Polo/Base",
                    "tipo": "Tipo",
                    "regiao": "Região",
                    "municipio_referencia": "Município de referência",
                    "observacao": "Observação",
                }
            )

            st.dataframe(
                polos,
                use_container_width=True,
                hide_index=True,
            )

    with tab3:
        if df_recursos.empty:
            st.info(
                "Nenhum recurso cadastrado na base neste momento."
            )
        else:
            recursos = df_recursos.copy()

            colunas = [
                "frente",
                "polo_base",
                "categoria",
                "descricao",
                "identificacao",
                "quantidade_planejada",
                "quantidade_disponivel",
                "status",
                "responsavel",
                "observacao",
            ]

            colunas = [
                c for c in colunas if c in recursos.columns
            ]

            recursos = recursos[colunas].rename(
                columns={
                    "frente": "Frente",
                    "polo_base": "Polo/Base",
                    "categoria": "Categoria",
                    "descricao": "Descrição",
                    "identificacao": "Identificação",
                    "quantidade_planejada": "Planejado",
                    "quantidade_disponivel": "Disponível",
                    "status": "Status",
                    "responsavel": "Responsável",
                    "observacao": "Observação",
                }
            )

            st.dataframe(
                recursos,
                use_container_width=True,
                hide_index=True,
            )


    with tab4:
        st.caption("Atualização individual com gravação no D1.")
        if df_pessoas.empty:
            st.info("Nenhuma pessoa cadastrada.")
        else:
            opts={f"{numero(r.get('id'))} — {texto(r.get('nome'))} — {texto(r.get('frente'))}":r for _,r in df_pessoas.sort_values("nome").iterrows()}
            sel=st.selectbox("Colaborador",list(opts),key="edit_pessoa")
            r=opts[sel]
            with st.form(f"form_pessoa_{numero(r.get('id'))}"):
                funcao=st.text_input("Função",value=texto(r.get("funcao"),""))
                situacao=st.text_input("Situação",value=texto(r.get("situacao"),""))
                c1,c2,c3,c4=st.columns(4)
                doc=c1.checkbox("Documentação enviada",value=bool(numero(r.get("documentacao_enviada"))))
                apr=c2.checkbox("Aprovado Aqua",value=bool(numero(r.get("aprovado_aqua"))))
                integ=c3.checkbox("Integrado",value=bool(numero(r.get("integrado"))))
                lib=c4.checkbox("Liberado campo",value=bool(numero(r.get("liberado_campo"))))
                adm=st.date_input("Data de admissão",value=converter_data(r.get("data_admissao")))
                obs=st.text_area("Observação",value=texto(r.get("observacao"),""))
                ok=st.form_submit_button("Salvar colaborador",use_container_width=True)
            if ok:
                payload={"funcao":funcao or None,"situacao":situacao or None,"documentacao_enviada":1 if doc else 0,"aprovado_aqua":1 if apr else 0,"integrado":1 if integ else 0,"liberado_campo":1 if lib else 0,"data_admissao":adm.isoformat() if adm else None,"observacao":obs or None,"atualizado_por":"Painel Mobilização"}
                try:
                    salvar_api(f"pessoas/{numero(r.get('id'))}",payload); st.success("Colaborador atualizado no D1."); limpar_recarregar()
                except Exception as e: st.error(f"Não foi possível salvar: {e}")

# ============================================================
# 6. CRONOGRAMA & RAMPAGEM
# ============================================================

elif pagina == "Cronograma & Rampagem":
    cabecalho(
        "Cronograma & Rampagem",
        "Prazos da implantação e evolução planejada versus mobilizada.",
    )

    tab1, tab2, tab3 = st.tabs(["Cronograma", "Rampagem", "Atualizar"])

    with tab1:
        if df_atividades.empty:
            st.info("Nenhuma atividade cadastrada.")
        else:
            cronograma = df_atividades.copy()

            f1, f2 = st.columns(2)

            frente = f1.selectbox(
                "Frente",
                ["Todas"]
                + sorted(
                    cronograma["frente"]
                    .dropna()
                    .unique()
                    .tolist()
                ),
                key="cron_frente",
            )

            situacao = f2.selectbox(
                "Situação",
                [
                    "Todas",
                    "Atrasadas",
                    "Prazo próximo",
                    "Aguardando Aqua",
                    "Em aberto",
                    "Concluídas",
                ],
                key="cron_situacao",
            )

            if frente != "Todas":
                cronograma = cronograma[
                    cronograma["frente"] == frente
                ]

            if situacao == "Atrasadas":
                cronograma = cronograma[cronograma["atrasada"]]

            elif situacao == "Prazo próximo":
                cronograma = cronograma[
                    cronograma["prazo_proximo"]
                ]

            elif situacao == "Aguardando Aqua":
                cronograma = cronograma[
                    cronograma["status"] == "Aguardando Aqua"
                ]

            elif situacao == "Em aberto":
                cronograma = cronograma[
                    ~cronograma["status"].isin(
                        ["Concluído", "Cancelado"]
                    )
                ]

            elif situacao == "Concluídas":
                cronograma = cronograma[
                    cronograma["status"] == "Concluído"
                ]

            cronograma["Início"] = cronograma[
                "data_inicio"
            ].apply(data_br)

            cronograma["Prazo"] = cronograma[
                "data_prevista"
            ].apply(data_br)

            cronograma["Conclusão"] = cronograma[
                "data_conclusao"
            ].apply(data_br)

            colunas = [
                "frente",
                "macroetapa",
                "atividade",
                "Início",
                "Prazo",
                "Conclusão",
                "dependencia",
                "prioridade",
                "status",
                "responsavel",
            ]

            colunas = [
                c for c in colunas if c in cronograma.columns
            ]

            cronograma = cronograma[colunas].rename(
                columns={
                    "frente": "Frente",
                    "macroetapa": "Macroetapa",
                    "atividade": "Atividade",
                    "dependencia": "Dependência",
                    "prioridade": "Prioridade",
                    "status": "Status",
                    "responsavel": "Responsável",
                }
            )

            st.dataframe(
                cronograma,
                use_container_width=True,
                hide_index=True,
                height=550,
            )

    with tab2:
        if df_rampagem.empty:
            st.info("Nenhuma rampagem cadastrada.")
        else:
            ramp = df_rampagem.copy()

            for campo in [
                "equipes_planejadas",
                "equipes_mobilizadas",
                "pessoas_planejadas",
                "pessoas_mobilizadas",
                "veiculos_planejados",
                "veiculos_mobilizados",
            ]:
                if campo not in ramp.columns:
                    ramp[campo] = 0

                ramp[campo] = pd.to_numeric(
                    ramp[campo], errors="coerce"
                ).fillna(0)

            frentes_ramp = sorted(
                ramp["frente"].dropna().unique().tolist()
            )

            filtro_frente = st.selectbox(
                "Frente",
                ["Todas"] + frentes_ramp,
                key="ramp_frente",
            )

            if filtro_frente != "Todas":
                ramp = ramp[ramp["frente"] == filtro_frente]

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Equipes planejadas",
                int(ramp["equipes_planejadas"].sum()),
            )

            c2.metric(
                "Equipes mobilizadas",
                int(ramp["equipes_mobilizadas"].sum()),
            )

            c3.metric(
                "Veículos planejados",
                int(ramp["veiculos_planejados"].sum()),
            )

            exibicao = ramp.copy()

            colunas = [
                "frente",
                "polo_base",
                "periodo",
                "equipes_planejadas",
                "equipes_mobilizadas",
                "pessoas_planejadas",
                "pessoas_mobilizadas",
                "veiculos_planejados",
                "veiculos_mobilizados",
                "observacao",
            ]

            colunas = [
                c for c in colunas if c in exibicao.columns
            ]

            exibicao = exibicao[colunas].rename(
                columns={
                    "frente": "Frente",
                    "polo_base": "Polo/Base",
                    "periodo": "Período",
                    "equipes_planejadas": "Equipes planejadas",
                    "equipes_mobilizadas": "Equipes mobilizadas",
                    "pessoas_planejadas": "Pessoas planejadas",
                    "pessoas_mobilizadas": "Pessoas mobilizadas",
                    "veiculos_planejados": "Veículos planejados",
                    "veiculos_mobilizados": "Veículos mobilizados",
                    "observacao": "Observação",
                }
            )

            st.dataframe(
                exibicao,
                use_container_width=True,
                hide_index=True,
            )

            if "periodo" in ramp.columns:
                grafico = (
                    ramp.groupby("periodo", as_index=False)[
                        [
                            "equipes_planejadas",
                            "equipes_mobilizadas",
                        ]
                    ]
                    .sum()
                    .set_index("periodo")
                )

                st.markdown("### Equipes — planejado x mobilizado")

                st.line_chart(grafico)


    with tab3:
        st.caption("Atualize a rampagem realizada. Os valores são gravados no D1.")
        if df_rampagem.empty:
            st.info("Nenhuma rampagem cadastrada.")
        else:
            opts={f"{numero(r.get('id'))} — {texto(r.get('frente'))} — {texto(r.get('periodo'))} — {texto(r.get('polo_base'))}":r for _,r in df_rampagem.iterrows()}
            sel=st.selectbox("Registro de rampagem",list(opts),key="edit_ramp")
            r=opts[sel]
            with st.form(f"form_ramp_{numero(r.get('id'))}"):
                c1,c2=st.columns(2)
                ep=c1.number_input("Equipes planejadas",0,value=numero(r.get("equipes_planejadas")),step=1)
                em=c2.number_input("Equipes mobilizadas",0,value=numero(r.get("equipes_mobilizadas")),step=1)
                c3,c4=st.columns(2)
                pp=c3.number_input("Pessoas planejadas",0,value=numero(r.get("pessoas_planejadas")),step=1)
                pm=c4.number_input("Pessoas mobilizadas",0,value=numero(r.get("pessoas_mobilizadas")),step=1)
                c5,c6=st.columns(2)
                vp=c5.number_input("Veículos planejados",0,value=numero(r.get("veiculos_planejados")),step=1)
                vm=c6.number_input("Veículos mobilizados",0,value=numero(r.get("veiculos_mobilizados")),step=1)
                obs=st.text_area("Observação",value=texto(r.get("observacao"),""))
                ok=st.form_submit_button("Salvar rampagem",use_container_width=True)
            if ok:
                payload={"equipes_planejadas":int(ep),"equipes_mobilizadas":int(em),"pessoas_planejadas":int(pp),"pessoas_mobilizadas":int(pm),"veiculos_planejados":int(vp),"veiculos_mobilizados":int(vm),"observacao":obs or None,"atualizado_por":"Painel Mobilização"}
                try:
                    salvar_api(f"rampagem/{numero(r.get('id'))}",payload); st.success("Rampagem atualizada no D1."); limpar_recarregar()
                except Exception as e: st.error(f"Não foi possível salvar: {e}")

# ============================================================
# 7. MODO REUNIÃO
# ============================================================

elif pagina == "Modo Reunião":
    cabecalho(
        "Modo Reunião",
        "Visão executiva para acompanhamento com a Aqua Pernambuco.",
    )

    st.markdown(
        "<div class='modo-reuniao'>"
        "Somente informações consolidadas. "
        "A base nominal de colaboradores não é exibida."
        "</div>",
        unsafe_allow_html=True,
    )

    dias = (GO_LIVE - date.today()).days

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Dias para Go-Live", dias)
    c2.metric("Mobilização geral", f"{totais['percentual']:.1f}%")
    c3.metric("Atividades concluídas", totais["concluidos"])
    c4.metric("Pontos aguardando Aqua", totais["aguardando_aqua"])

    st.markdown("## Mobilização das frentes")

    if not df_resumo.empty:
        for _, row in df_resumo.iterrows():
            frente = texto(row.get("frente"))
            total = numero(row.get("total"))
            concluidos = numero(row.get("concluidos"))
            cancelados = numero(row.get("cancelados"))

            pct = percentual_mobilizacao(
                total, concluidos, cancelados
            )

            st.markdown(f"### {frente}")
            st.progress(min(max(pct / 100, 0), 1))
            st.caption(
                f"{concluidos} de "
                f"{max(total - cancelados, 0)} atividades concluídas "
                f"· {pct:.1f}%"
            )

    esquerda, direita = st.columns(2)

    with esquerda:
        st.markdown("## Pontos que exigem ação")

        criticos = pontos_criticos(df_atividades, 8)

        if criticos.empty:
            st.success("Nenhum ponto crítico identificado.")
        else:
            for _, row in criticos.iterrows():
                st.markdown(
                    f"""
                    <div class="card">
                        <div class="card-titulo">
                            {texto(row.get("atividade"))}
                        </div>
                        <div class="card-texto">
                            <b>{texto(row.get("frente"))}</b>
                            · {texto(row.get("status"))}<br>
                            Responsável:
                            {texto(row.get("responsavel"))}
                            · Prazo:
                            {data_br(row.get("data_prevista"))}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with direita:
        st.markdown("## Próximos passos")

        if not df_atividades.empty:
            proximos = df_atividades[
                ~df_atividades["status"].isin(
                    ["Concluído", "Cancelado"]
                )
            ].copy()

            proximos["proximo"] = proximos.apply(
                proximo_passo, axis=1
            )

            proximos = proximos[
                proximos["proximo"] != "—"
            ].sort_values(
                ["ordem_prioridade", "data_prevista_dt"],
                na_position="last",
            ).head(8)

            if proximos.empty:
                st.info("Nenhum próximo passo registrado.")
            else:
                for _, row in proximos.iterrows():
                    st.markdown(
                        f"""
                        <div class="card">
                            <div class="card-titulo">
                                {texto(row.get("frente"))}
                                · {texto(row.get("atividade"))}
                            </div>
                            <div class="card-texto">
                                {proximo_passo(row)}<br>
                                <b>Responsável:</b>
                                {texto(row.get("responsavel"))}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    st.markdown("## Macroetapas — visão executiva")
    grafico_macroetapas(df_atividades, "reuniao")

    st.markdown("## Pessoas — visão quantitativa")

    total_pessoas = len(df_pessoas)

    def reuniao_flag(campo):
        if df_pessoas.empty or campo not in df_pessoas.columns:
            return 0

        return int(
            pd.to_numeric(
                df_pessoas[campo], errors="coerce"
            ).fillna(0).sum()
        )

    p1, p2, p3, p4 = st.columns(4)

    p1.metric("Cadastrados", total_pessoas)
    p2.metric(
        "Documentação enviada",
        reuniao_flag("documentacao_enviada"),
    )
    p3.metric(
        "Aprovados Aqua",
        reuniao_flag("aprovado_aqua"),
    )
    p4.metric(
        "Liberados para campo",
        reuniao_flag("liberado_campo"),
    )

    st.markdown("## Rampagem")

    if df_rampagem.empty:
        st.info("Nenhuma rampagem cadastrada.")
    else:
        ramp_reuniao = df_rampagem.copy()

        colunas = [
            "frente",
            "periodo",
            "equipes_planejadas",
            "equipes_mobilizadas",
            "veiculos_planejados",
            "veiculos_mobilizados",
        ]

        colunas = [
            c for c in colunas if c in ramp_reuniao.columns
        ]

        ramp_reuniao = ramp_reuniao[colunas].rename(
            columns={
                "frente": "Frente",
                "periodo": "Período",
                "equipes_planejadas": "Equipes planejadas",
                "equipes_mobilizadas": "Equipes mobilizadas",
                "veiculos_planejados": "Veículos planejados",
                "veiculos_mobilizados": "Veículos mobilizados",
            }
        )

        st.dataframe(
            ramp_reuniao,
            use_container_width=True,
            hide_index=True,
        )

# ============================================================
# RODAPÉ
# ============================================================

st.markdown(
    f"""
    <div class="rodape">
        V0 — versão-base oficial ·
        Dados carregados da base estruturada de mobilização ·
        Go-Live: 26/10/2026
    </div>
    """,
    unsafe_allow_html=True,
)
