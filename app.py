import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date
import plotly.graph_objects as go

# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="Mobilização | Aqua Pernambuco – Enorsul",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

API = "https://aqua-mobilizacao-api.leandro-cifra.workers.dev"
GO_LIVE = date(2026, 10, 26)

STATUS = [
    "Não iniciado",
    "Em andamento",
    "Aguardando Aqua",
    "Concluído",
    "Cancelado",
]

PRIORIDADES = [
    "Crítica",
    "Alta",
    "Média",
    "Baixa",
]

# ============================================================
# BLACK PIANO
# ============================================================

st.markdown(
    """
<style>

/* =========================================================
   BASE
========================================================= */

:root {
    --bg: #050506;
    --bg2: #08080a;
    --card: #0d0d10;
    --card2: #121216;
    --line: #292930;
    --line2: #36363e;
    --text: #f5f5f7;
    --muted: #9b9ba6;
    --red: #e31b2d;
    --green: #37c98b;
    --yellow: #e7bb55;
    --blue: #559fd0;
}

html,
body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background:
        radial-gradient(
            circle at 80% -15%,
            #24242a 0%,
            #0a0a0d 31%,
            #050506 68%
        ) !important;
    color: var(--text) !important;
}

[data-testid="stAppViewContainer"] > .main {
    background: transparent !important;
}

[data-testid="stHeader"] {
    background: rgba(5,5,6,.78) !important;
    backdrop-filter: blur(18px);
}

.block-container {
    max-width: 1580px;
    padding-top: 1.2rem;
    padding-bottom: 5rem;
}

/* =========================================================
   SIDEBAR
========================================================= */

[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            #09090b 0%,
            #050506 100%
        ) !important;

    border-right: 1px solid #202025;
}

[data-testid="stSidebar"] * {
    color: #ededf0 !important;
}

/* =========================================================
   TEXTOS
========================================================= */

h1, h2, h3, h4 {
    color: #ffffff !important;
    letter-spacing: -0.025em;
}

h1 {
    font-size: 2.05rem !important;
    font-weight: 780 !important;
}

h2 {
    font-size: 1.28rem !important;
    margin-top: 1.5rem !important;
}

p,
span,
label {
    color: #dedee3;
}

.eyebrow {
    color: var(--red);
    font-size: .72rem;
    font-weight: 800;
    letter-spacing: .13em;
    text-transform: uppercase;
    margin-bottom: 5px;
}

.subtitle {
    color: #9696a2;
    font-size: .92rem;
    margin-top: -9px;
    margin-bottom: 20px;
}

/* =========================================================
   MÉTRICAS
========================================================= */

[data-testid="stMetric"] {
    background:
        linear-gradient(
            145deg,
            rgba(29,29,34,.96),
            rgba(8,8,10,.98)
        ) !important;

    border: 1px solid #2c2c33;
    border-radius: 18px;
    padding: 16px 18px;

    box-shadow:
        inset 0 1px 0 rgba(255,255,255,.07),
        0 14px 36px rgba(0,0,0,.30);
}

[data-testid="stMetricLabel"] {
    color: #a2a2ad !important;
    font-weight: 600;
}

[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-weight: 760;
}

/* =========================================================
   INPUTS - EVITA FUNDO BRANCO
========================================================= */

[data-baseweb="input"] > div,
[data-baseweb="base-input"],
[data-baseweb="select"] > div,
[data-baseweb="textarea"] > div,
[data-baseweb="popover"],
[data-baseweb="menu"],
[data-baseweb="select"] {
    background-color: #101013 !important;
    color: #f5f5f7 !important;
    border-color: #34343c !important;
}

input,
textarea {
    background-color: #101013 !important;
    color: #f5f5f7 !important;
    -webkit-text-fill-color: #f5f5f7 !important;
}

[data-baseweb="select"] span {
    color: #f5f5f7 !important;
}

[data-baseweb="menu"] {
    background: #101013 !important;
}

[data-baseweb="menu"] li {
    background: #101013 !important;
    color: white !important;
}

[data-baseweb="menu"] li:hover {
    background: #202026 !important;
}

/* DATE INPUT */

[data-testid="stDateInput"] input {
    background: #101013 !important;
    color: white !important;
}

/* NUMBER INPUT */

[data-testid="stNumberInput"] input {
    background: #101013 !important;
    color: white !important;
}

/* =========================================================
   BOTÕES
========================================================= */

div.stButton > button,
div.stFormSubmitButton > button {
    border-radius: 12px !important;
    border: 1px solid #383840 !important;
    background:
        linear-gradient(
            145deg,
            #1a1a1f,
            #0c0c0f
        ) !important;
    color: #ffffff !important;
    font-weight: 650 !important;
}

div.stButton > button:hover,
div.stFormSubmitButton > button:hover {
    border-color: var(--red) !important;
    box-shadow: 0 0 0 1px rgba(227,27,45,.18);
}

/* =========================================================
   TABELAS
========================================================= */

[data-testid="stDataFrame"] {
    border: 1px solid #28282f;
    border-radius: 16px;
    overflow: hidden;
    background: #09090b !important;
}

[data-testid="stDataFrame"] * {
    color: #ededf0;
}

/* =========================================================
   EXPANDER
========================================================= */

[data-testid="stExpander"] {
    background:
        linear-gradient(
            145deg,
            rgba(22,22,27,.97),
            rgba(8,8,10,.98)
        ) !important;

    border: 1px solid #292930 !important;
    border-radius: 16px !important;
    margin-bottom: 9px;
}

[data-testid="stExpander"] details {
    background: transparent !important;
}

/* =========================================================
   FORM
========================================================= */

[data-testid="stForm"] {
    background:
        linear-gradient(
            145deg,
            rgba(20,20,24,.98),
            rgba(7,7,9,.99)
        ) !important;

    border: 1px solid #292930 !important;
    border-radius: 18px !important;
    padding: 18px !important;
}

/* =========================================================
   TABS
========================================================= */

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    background: #0e0e11 !important;
    border: 1px solid #292930 !important;
    border-radius: 12px !important;
    padding: 9px 16px !important;
}

.stTabs [aria-selected="true"] {
    border-color: var(--red) !important;
    box-shadow:
        inset 0 -2px 0 var(--red);
}

/* =========================================================
   CARDS
========================================================= */

.piano-card {
    background:
        linear-gradient(
            145deg,
            rgba(24,24,29,.96),
            rgba(7,7,9,.99)
        );

    border: 1px solid #292930;
    border-radius: 18px;
    padding: 17px 18px;
    margin: 9px 0;

    box-shadow:
        inset 0 1px 0 rgba(255,255,255,.06),
        0 12px 30px rgba(0,0,0,.25);
}

.piano-title {
    font-weight: 720;
    color: white;
    font-size: .98rem;
    margin-bottom: 7px;
}

.piano-body {
    color: #aaaab4;
    font-size: .87rem;
    line-height: 1.5;
}

/* =========================================================
   PILLS
========================================================= */

.pill {
    display: inline-block;
    border: 1px solid #34343c;
    border-radius: 999px;
    padding: 3px 8px;
    margin: 2px 4px 5px 0;
    font-size: .70rem;
    color: #d8d8dd;
    background: #111115;
}

.red {
    border-color: #65232c;
    color: #ff8b97;
    background: #1d0c10;
}

.green {
    border-color: #20513d;
    color: #7fe0b4;
    background: #091811;
}

.yellow {
    border-color: #604c1c;
    color: #ffd477;
    background: #1b1608;
}

.blue {
    border-color: #234a63;
    color: #8ac9ef;
    background: #09161f;
}

/* =========================================================
   ALERTS
========================================================= */

[data-testid="stAlert"] {
    background: #101013 !important;
    border-radius: 14px !important;
}

/* =========================================================
   PROGRESS
========================================================= */

[data-testid="stProgress"] > div > div {
    background-color: #26262c !important;
}

[data-testid="stProgress"] > div > div > div {
    background-color: var(--red) !important;
}

/* =========================================================
   HERO
========================================================= */

.hero {
    background:
        linear-gradient(
            110deg,
            rgba(31,31,37,.95),
            rgba(8,8,10,.98)
        );

    border: 1px solid #2c2c33;
    border-radius: 22px;
    padding: 21px 23px;
    margin-bottom: 18px;

    box-shadow:
        inset 0 1px 0 rgba(255,255,255,.08),
        0 20px 45px rgba(0,0,0,.28);
}

.hero strong {
    color: white;
}

.hero span {
    color: #a5a5af;
}

.small-note {
    color: #777783;
    font-size: .76rem;
}

hr {
    border-color: #242429 !important;
}

</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# API
# ============================================================

def api_get(rota):
    try:
        r = requests.get(
            f"{API}{rota}",
            timeout=20
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(
            f"Erro ao consultar {rota}: {e}"
        )
        return []


def api_put(rota, dados):
    try:
        r = requests.put(
            f"{API}{rota}",
            json=dados,
            timeout=25
        )

        try:
            retorno = r.json()
        except Exception:
            retorno = {
                "ok": False,
                "erro": r.text
            }

        if not r.ok:
            return False, retorno

        return True, retorno

    except Exception as e:
        return False, {
            "ok": False,
            "erro": str(e)
        }


@st.cache_data(ttl=20)
def carregar_dados():
    return {
        "frentes": api_get("/frentes"),
        "atividades": api_get("/atividades"),
        "polos": api_get("/polos"),
        "pessoas": api_get("/pessoas"),
        "recursos": api_get("/recursos"),
        "rampagem": api_get("/rampagem"),
        "resumo": api_get("/resumo"),
        "historico": api_get("/historico?limite=300"),
    }


def recarregar():
    st.cache_data.clear()
    st.rerun()


dados = carregar_dados()

frentes = pd.DataFrame(dados["frentes"])
atividades = pd.DataFrame(dados["atividades"])
polos = pd.DataFrame(dados["polos"])
pessoas = pd.DataFrame(dados["pessoas"])
recursos = pd.DataFrame(dados["recursos"])
rampagem = pd.DataFrame(dados["rampagem"])
historico = pd.DataFrame(dados["historico"])


# ============================================================
# FUNÇÕES
# ============================================================

def txt(v):
    if v is None:
        return ""
    if pd.isna(v):
        return ""
    return str(v)


def inteiro(v, padrao=0):
    try:
        return int(v)
    except Exception:
        return padrao


def data_valor(v):
    if not v:
        return None

    try:
        return pd.to_datetime(v).date()
    except Exception:
        return None


def data_api(v):
    if v is None:
        return None

    if hasattr(v, "strftime"):
        return v.strftime("%Y-%m-%d")

    return str(v)


def formatar_data(v):
    if not v:
        return "—"

    try:
        return pd.to_datetime(v).strftime(
            "%d/%m/%Y"
        )
    except Exception:
        return str(v)


def cabecalho(titulo, subtitulo):
    st.markdown(
        f"""
        <div class="eyebrow">
            V0 · BLACK PIANO
        </div>
        <h1>{titulo}</h1>
        <div class="subtitle">
            {subtitulo}
        </div>
        """,
        unsafe_allow_html=True,
    )


def resumo_df(df):
    if df.empty:
        return {
            "total": 0,
            "concluidos": 0,
            "andamento": 0,
            "aqua": 0,
            "nao": 0,
            "cancelados": 0,
            "pct": 0,
        }

    cont = df["status"].value_counts()

    total = len(df)
    concluidos = inteiro(
        cont.get("Concluído", 0)
    )
    cancelados = inteiro(
        cont.get("Cancelado", 0)
    )

    denominador = total - cancelados

    pct = (
        concluidos / denominador * 100
        if denominador > 0
        else 0
    )

    return {
        "total": total,
        "concluidos": concluidos,
        "andamento": inteiro(
            cont.get("Em andamento", 0)
        ),
        "aqua": inteiro(
            cont.get("Aguardando Aqua", 0)
        ),
        "nao": inteiro(
            cont.get("Não iniciado", 0)
        ),
        "cancelados": cancelados,
        "pct": pct,
    }


def preparar_atividades(df):
    if df.empty:
        return df

    x = df.copy()

    x["data_prevista_dt"] = pd.to_datetime(
        x["data_prevista"],
        errors="coerce"
    )

    hoje = pd.Timestamp(date.today())

    x["atrasada"] = (
        x["data_prevista_dt"].notna()
        & (x["data_prevista_dt"] < hoje)
        & ~x["status"].isin(
            ["Concluído", "Cancelado"]
        )
    )

    x["prazo_proximo"] = (
        x["data_prevista_dt"].notna()
        & (x["data_prevista_dt"] >= hoje)
        & (
            x["data_prevista_dt"]
            <= hoje + pd.Timedelta(days=7)
        )
        & ~x["status"].isin(
            ["Concluído", "Cancelado"]
        )
    )

    prioridade_ordem = {
        "Crítica": 0,
        "Alta": 1,
        "Média": 2,
        "Baixa": 3,
    }

    x["prioridade_ordem"] = (
        x["prioridade"]
        .map(prioridade_ordem)
        .fillna(9)
    )

    return x


atividades = preparar_atividades(
    atividades
)


def pontos_criticos(df, limite=8):
    if df.empty:
        return df

    x = df[
        ~df["status"].isin(
            ["Concluído", "Cancelado"]
        )
    ].copy()

    if x.empty:
        return x

    def nivel(r):
        if r["atrasada"]:
            return 0

        if r["status"] == "Aguardando Aqua":
            return 1

        if r["prazo_proximo"]:
            return 2

        if r["prioridade"] == "Crítica":
            return 3

        if r["prioridade"] == "Alta":
            return 4

        return 5

    x["nivel"] = x.apply(
        nivel,
        axis=1
    )

    return (
        x.sort_values(
            [
                "nivel",
                "prioridade_ordem",
                "data_prevista_dt",
            ],
            na_position="last",
        )
        .head(limite)
    )


def badges(r):
    lista = []

    if bool(r.get("atrasada", False)):
        lista.append(
            '<span class="pill red">ATRASADA</span>'
        )

    if (
        r.get("status")
        == "Aguardando Aqua"
    ):
        lista.append(
            '<span class="pill yellow">'
            'AGUARDANDO AQUA'
            '</span>'
        )

    if bool(
        r.get("prazo_proximo", False)
    ):
        lista.append(
            '<span class="pill blue">'
            'PRAZO PRÓXIMO'
            '</span>'
        )

    if (
        r.get("status")
        == "Concluído"
    ):
        lista.append(
            '<span class="pill green">'
            'CONCLUÍDO'
            '</span>'
        )

    prioridade = txt(
        r.get("prioridade")
    )

    if prioridade:
        lista.append(
            f'<span class="pill">'
            f'{prioridade}'
            f'</span>'
        )

    return "".join(lista)


def cards_criticos(df, limite=6):
    x = pontos_criticos(
        df,
        limite
    )

    if x.empty:
        st.success(
            "Nenhum ponto crítico identificado."
        )
        return

    for _, r in x.iterrows():
        acao = (
            txt(r.get("proximo_passo_manual"))
            or txt(r.get("pendencia_acao"))
        )

        html = (
            f'<div class="piano-card">'
            f'<div class="piano-title">{txt(r.get("atividade"))}</div>'
            f'{badges(r)}'
            f'<div class="piano-body">'
            f'<b>{txt(r.get("frente"))}</b> · {txt(r.get("status"))}<br>'
            f'Responsável: {txt(r.get("responsavel")) or "—"} '
            f'· Prazo: {formatar_data(r.get("data_prevista"))}'
            f'{"<br><br>" + acao if acao else ""}'
            f'</div></div>'
        )
        st.markdown(html, unsafe_allow_html=True)


def grafico_status(df):
    r = resumo_df(df)

    labels = [
        "Concluído",
        "Em andamento",
        "Aguardando Aqua",
        "Não iniciado",
    ]

    valores = [
        r["concluidos"],
        r["andamento"],
        r["aqua"],
        r["nao"],
    ]

    fig = go.Figure(
        go.Bar(
            x=valores,
            y=labels,
            orientation="h",
            text=valores,
            textposition="auto",
            marker_color=[
                "#37c98b",
                "#559fd0",
                "#e7bb55",
                "#e31b2d",
            ],
        )
    )

    fig.update_layout(
        height=275,
        margin=dict(
            l=0,
            r=10,
            t=10,
            b=0
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#d7d7dc",
        xaxis=dict(
            visible=False,
            showgrid=False
        ),
        yaxis=dict(
            showgrid=False,
            autorange="reversed"
        ),
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False
        },
    )


def tabela_atividades(df):
    if df.empty:
        st.info(
            "Nenhuma atividade encontrada."
        )
        return

    x = df.copy()

    x["Prazo"] = (
        x["data_prevista"]
        .apply(formatar_data)
    )

    x["%"] = (
        x["percentual"]
        .fillna(0)
        .astype(int)
    )

    colunas = [
        "macroetapa",
        "atividade",
        "prioridade",
        "status",
        "%",
        "responsavel",
        "dependencia",
        "Prazo",
    ]

    nomes = {
        "macroetapa": "Macroetapa",
        "atividade": "Atividade",
        "prioridade": "Prioridade",
        "status": "Status",
        "responsavel": "Responsável",
        "dependencia": "Dependência",
    }

    st.dataframe(
        x[colunas].rename(
            columns=nomes
        ),
        use_container_width=True,
        hide_index=True,
        height=480,
    )


# ============================================================
# EDITOR DE ATIVIDADE
# ============================================================

def editor_atividade(df, chave):
    if df.empty:
        st.info(
            "Nenhuma atividade disponível."
        )
        return

    opcoes = {}

    for _, r in df.iterrows():
        rotulo = (
            f'{int(r["id"])} · '
            f'{txt(r["atividade"])}'
        )

        opcoes[rotulo] = int(
            r["id"]
        )

    escolha = st.selectbox(
        "Selecione a atividade",
        list(opcoes.keys()),
        key=f"atividade_{chave}",
    )

    atividade_id = opcoes[
        escolha
    ]

    r = df[
        df["id"] == atividade_id
    ].iloc[0]

    status_atual = txt(
        r.get("status")
    )

    prioridade_atual = txt(
        r.get("prioridade")
    )

    with st.form(
        f"form_atividade_{chave}_{atividade_id}"
    ):

        st.markdown(
            f"### {txt(r.get('atividade'))}"
        )

        c1, c2, c3 = st.columns(
            [1, 1, 1]
        )

        status = c1.selectbox(
            "Status",
            STATUS,
            index=(
                STATUS.index(status_atual)
                if status_atual in STATUS
                else 0
            ),
        )

        prioridade = c2.selectbox(
            "Prioridade",
            PRIORIDADES,
            index=(
                PRIORIDADES.index(
                    prioridade_atual
                )
                if prioridade_atual
                in PRIORIDADES
                else 2
            ),
        )

        percentual = c3.number_input(
            "Percentual",
            min_value=0,
            max_value=100,
            value=inteiro(
                r.get("percentual")
            ),
            step=5,
        )

        c1, c2 = st.columns(2)

        responsavel = c1.text_input(
            "Responsável",
            value=txt(
                r.get("responsavel")
            ),
        )

        dependencia = c2.text_input(
            "Dependência",
            value=txt(
                r.get("dependencia")
            ),
        )

        c1, c2, c3 = st.columns(3)

        inicio_atual = data_valor(
            r.get("data_inicio")
        )

        prevista_atual = data_valor(
            r.get("data_prevista")
        )

        conclusao_atual = data_valor(
            r.get("data_conclusao")
        )

        data_inicio = c1.date_input(
            "Data de início",
            value=inicio_atual,
            format="DD/MM/YYYY",
        )

        data_prevista = c2.date_input(
            "Prazo",
            value=prevista_atual,
            format="DD/MM/YYYY",
        )

        data_conclusao = c3.date_input(
            "Conclusão",
            value=conclusao_atual,
            format="DD/MM/YYYY",
        )

        pendencia = st.text_area(
            "Pendência / Ação",
            value=txt(
                r.get("pendencia_acao")
            ),
            height=85,
        )

        proximo = st.text_area(
            "Próximo passo",
            value=txt(
                r.get(
                    "proximo_passo_manual"
                )
            ),
            height=85,
        )

        criterio = st.text_area(
            "Critério de aceite",
            value=txt(
                r.get("criterio_aceite")
            ),
            height=85,
        )

        evidencia = st.text_area(
            "Evidência",
            value=txt(
                r.get("evidencia")
            ),
            height=85,
        )

        observacao = st.text_area(
            "Observação",
            value=txt(
                r.get("observacao")
            ),
            height=100,
        )

        atualizado_por = st.text_input(
            "Atualizado por",
            value="Equipe Enorsul",
        )

        salvar = st.form_submit_button(
            "Salvar alterações",
            use_container_width=True,
        )

        if salvar:
            payload = {
                "status": status,
                "prioridade": prioridade,
                "percentual": int(
                    percentual
                ),
                "responsavel": (
                    responsavel or None
                ),
                "dependencia": (
                    dependencia or None
                ),
                "data_inicio": data_api(
                    data_inicio
                ),
                "data_prevista": data_api(
                    data_prevista
                ),
                "data_conclusao": data_api(
                    data_conclusao
                ),
                "pendencia_acao": (
                    pendencia or None
                ),
                "proximo_passo_manual": (
                    proximo or None
                ),
                "criterio_aceite": (
                    criterio or None
                ),
                "evidencia": (
                    evidencia or None
                ),
                "observacao": (
                    observacao or None
                ),
                "atualizado_por": (
                    atualizado_por
                    or "Equipe Enorsul"
                ),
            }

            ok, retorno = api_put(
                f"/atividades/{atividade_id}",
                payload,
            )

            if ok:
                st.success(
                    "Alterações gravadas no D1."
                )

                st.cache_data.clear()

                st.rerun()

            else:
                st.error(
                    retorno.get(
                        "erro",
                        "Não foi possível salvar."
                    )
                )


# ============================================================
# EDITOR PESSOAS
# ============================================================

def editor_pessoa():
    if pessoas.empty:
        st.info(
            "Nenhuma pessoa cadastrada."
        )
        return

    opcoes = {}

    for _, r in pessoas.iterrows():
        rotulo = (
            f'{int(r["id"])} · '
            f'{txt(r["nome"])}'
        )

        opcoes[rotulo] = int(
            r["id"]
        )

    escolha = st.selectbox(
        "Selecione o colaborador",
        list(opcoes.keys()),
        key="editor_pessoa",
    )

    pessoa_id = opcoes[
        escolha
    ]

    r = pessoas[
        pessoas["id"] == pessoa_id
    ].iloc[0]

    with st.form(
        f"pessoa_{pessoa_id}"
    ):

        st.markdown(
            f"### {txt(r.get('nome'))}"
        )

        c1, c2 = st.columns(2)

        funcao = c1.text_input(
            "Função",
            value=txt(
                r.get("funcao")
            ),
        )

        situacao = c2.text_input(
            "Situação",
            value=txt(
                r.get("situacao")
            ),
        )

        c1, c2, c3, c4 = st.columns(4)

        doc = c1.checkbox(
            "Documentação enviada",
            value=bool(
                inteiro(
                    r.get(
                        "documentacao_enviada"
                    )
                )
            ),
        )

        aprovado = c2.checkbox(
            "Aprovado Aqua",
            value=bool(
                inteiro(
                    r.get(
                        "aprovado_aqua"
                    )
                )
            ),
        )

        integrado = c3.checkbox(
            "Integrado",
            value=bool(
                inteiro(
                    r.get(
                        "integrado"
                    )
                )
            ),
        )

        campo = c4.checkbox(
            "Liberado para campo",
            value=bool(
                inteiro(
                    r.get(
                        "liberado_campo"
                    )
                )
            ),
        )

        adm_atual = data_valor(
            r.get("data_admissao")
        )

        admissao = st.date_input(
            "Data de admissão",
            value=adm_atual,
            format="DD/MM/YYYY",
        )

        observacao = st.text_area(
            "Observação",
            value=txt(
                r.get("observacao")
            ),
        )

        atualizado_por = st.text_input(
            "Atualizado por",
            value="Equipe Enorsul",
            key=f"por_pessoa_{pessoa_id}",
        )

        salvar = st.form_submit_button(
            "Salvar colaborador",
            use_container_width=True,
        )

        if salvar:
            payload = {
                "funcao": (
                    funcao or None
                ),
                "situacao": (
                    situacao or None
                ),
                "documentacao_enviada": (
                    1 if doc else 0
                ),
                "aprovado_aqua": (
                    1 if aprovado else 0
                ),
                "integrado": (
                    1 if integrado else 0
                ),
                "liberado_campo": (
                    1 if campo else 0
                ),
                "data_admissao": data_api(
                    admissao
                ),
                "observacao": (
                    observacao or None
                ),
                "atualizado_por": (
                    atualizado_por
                    or "Equipe Enorsul"
                ),
            }

            ok, retorno = api_put(
                f"/pessoas/{pessoa_id}",
                payload,
            )

            if ok:
                st.success(
                    "Colaborador atualizado."
                )
                st.cache_data.clear()
                st.rerun()

            else:
                st.error(
                    retorno.get(
                        "erro",
                        "Erro ao salvar."
                    )
                )


# ============================================================
# EDITOR RAMPAGEM
# ============================================================

def editor_rampagem():
    if rampagem.empty:
        st.info(
            "Nenhuma rampagem cadastrada."
        )
        return

    opcoes = {}

    for _, r in rampagem.iterrows():
        rotulo = (
            f'{int(r["id"])} · '
            f'{txt(r.get("frente"))} · '
            f'{txt(r.get("periodo"))}'
        )

        opcoes[rotulo] = int(
            r["id"]
        )

    escolha = st.selectbox(
        "Selecione a linha",
        list(opcoes.keys()),
        key="editor_rampagem",
    )

    rid = opcoes[
        escolha
    ]

    r = rampagem[
        rampagem["id"] == rid
    ].iloc[0]

    with st.form(
        f"rampagem_{rid}"
    ):

        st.markdown(
            f"### {txt(r.get('frente'))}"
            f" · {txt(r.get('periodo'))}"
        )

        c1, c2 = st.columns(2)

        equipes_plan = c1.number_input(
            "Equipes planejadas",
            min_value=0,
            value=inteiro(
                r.get(
                    "equipes_planejadas"
                )
            ),
        )

        equipes_mob = c2.number_input(
            "Equipes mobilizadas",
            min_value=0,
            value=inteiro(
                r.get(
                    "equipes_mobilizadas"
                )
            ),
        )

        c1, c2 = st.columns(2)

        pessoas_plan = c1.number_input(
            "Pessoas planejadas",
            min_value=0,
            value=inteiro(
                r.get(
                    "pessoas_planejadas"
                )
            ),
        )

        pessoas_mob = c2.number_input(
            "Pessoas mobilizadas",
            min_value=0,
            value=inteiro(
                r.get(
                    "pessoas_mobilizadas"
                )
            ),
        )

        c1, c2 = st.columns(2)

        veiculos_plan = c1.number_input(
            "Veículos planejados",
            min_value=0,
            value=inteiro(
                r.get(
                    "veiculos_planejados"
                )
            ),
        )

        veiculos_mob = c2.number_input(
            "Veículos mobilizados",
            min_value=0,
            value=inteiro(
                r.get(
                    "veiculos_mobilizados"
                )
            ),
        )

        observacao = st.text_area(
            "Observação",
            value=txt(
                r.get("observacao")
            ),
        )

        atualizado_por = st.text_input(
            "Atualizado por",
            value="Equipe Enorsul",
            key=f"por_ramp_{rid}",
        )

        salvar = st.form_submit_button(
            "Salvar rampagem",
            use_container_width=True,
        )

        if salvar:
            payload = {
                "equipes_planejadas":
                    int(equipes_plan),

                "equipes_mobilizadas":
                    int(equipes_mob),

                "pessoas_planejadas":
                    int(pessoas_plan),

                "pessoas_mobilizadas":
                    int(pessoas_mob),

                "veiculos_planejados":
                    int(veiculos_plan),

                "veiculos_mobilizados":
                    int(veiculos_mob),

                "observacao":
                    observacao or None,

                "atualizado_por":
                    atualizado_por
                    or "Equipe Enorsul",
            }

            ok, retorno = api_put(
                f"/rampagem/{rid}",
                payload,
            )

            if ok:
                st.success(
                    "Rampagem atualizada."
                )
                st.cache_data.clear()
                st.rerun()

            else:
                st.error(
                    retorno.get(
                        "erro",
                        "Erro ao salvar."
                    )
                )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        "## ◆ Mobilização"
    )

    st.caption(
        "Aqua Pernambuco · Enorsul"
    )

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

    dias = (
        GO_LIVE - date.today()
    ).days

    st.metric(
        "Go-Live",
        "26/10/2026"
    )

    st.caption(
        f"{dias} dias para entrada"
    )

    if st.button(
        "↻ Atualizar dados",
        use_container_width=True,
    ):
        recarregar()

    st.caption(
        "Dados persistidos no Cloudflare D1"
    )


# ============================================================
# VISÃO GERAL
# ============================================================

if pagina == "Visão Geral":

    cabecalho(
        "Mobilização | Aqua Pernambuco – Enorsul",
        "Visão executiva consolidada da implantação.",
    )

    r = resumo_df(
        atividades
    )

    st.markdown(
        """
        <div class="hero">
            <strong>
                Painel operacional conectado ao D1.
            </strong>
            <br>
            <span>
                As alterações realizadas nas telas
                operacionais atualizam esta visão.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c = st.columns(6)

    metricas = [
        (
            "Dias para Go-Live",
            dias
        ),
        (
            "% Mobilização",
            f'{r["pct"]:.1f}%'
        ),
        (
            "Concluídos",
            r["concluidos"]
        ),
        (
            "Em andamento",
            r["andamento"]
        ),
        (
            "Aguardando Aqua",
            r["aqua"]
        ),
        (
            "Não iniciados",
            r["nao"]
        ),
    ]

    for coluna, metrica in zip(
        c,
        metricas
    ):
        coluna.metric(
            metrica[0],
            metrica[1]
        )

    st.markdown(
        "## Mobilização por frente"
    )

    linhas = []

    for frente in [
        "Leitura",
        "Cobrança",
        "Hidrometria",
    ]:

        z = resumo_df(
            atividades[
                atividades["frente"]
                == frente
            ]
        )

        linhas.append(
            {
                "Frente": frente,
                "Total": z["total"],
                "Concluído":
                    z["concluidos"],
                "Em andamento":
                    z["andamento"],
                "Aguardando Aqua":
                    z["aqua"],
                "Não iniciado":
                    z["nao"],
                "Mobilização":
                    f'{z["pct"]:.1f}%',
            }
        )

    st.dataframe(
        pd.DataFrame(linhas),
        use_container_width=True,
        hide_index=True,
    )

    c1, c2 = st.columns(
        [1.08, .92]
    )

    with c1:
        st.markdown(
            "## Pontos críticos"
        )

        cards_criticos(
            atividades,
            8
        )

    with c2:
        st.markdown(
            "## Distribuição atual"
        )

        grafico_status(
            atividades
        )

        st.markdown(
            "## Próximos passos"
        )

        proximos = (
            pontos_criticos(
                atividades,
                5
            )
        )

        for _, linha in proximos.iterrows():

            acao = (
                txt(
                    linha.get(
                        "proximo_passo_manual"
                    )
                )
                or txt(
                    linha.get(
                        "pendencia_acao"
                    )
                )
            )

            st.markdown(
                f"""
                <div class="piano-card">
                    <div class="piano-title">
                        {txt(
                            linha.get(
                                "atividade"
                            )
                        )}
                    </div>
                    <div class="piano-body">
                        {acao or "Sem próximo passo registrado."}
                        <br>
                        <b>Responsável:</b>
                        {
                            txt(
                                linha.get(
                                    "responsavel"
                                )
                            )
                            or "—"
                        }
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ============================================================
# LEITURA / COBRANÇA / HIDROMETRIA
# ============================================================

elif pagina in [
    "Leitura",
    "Cobrança",
    "Hidrometria",
]:

    frente = pagina

    df = atividades[
        atividades["frente"]
        == frente
    ].copy()

    cabecalho(
        frente,
        f"Acompanhamento operacional e atualização de {frente.lower()}.",
    )

    r = resumo_df(df)

    c = st.columns(5)

    metricas = [
        (
            "Mobilização",
            f'{r["pct"]:.1f}%'
        ),
        (
            "Concluídos",
            r["concluidos"]
        ),
        (
            "Em andamento",
            r["andamento"]
        ),
        (
            "Aguardando Aqua",
            r["aqua"]
        ),
        (
            "Não iniciados",
            r["nao"]
        ),
    ]

    for coluna, metrica in zip(
        c,
        metricas
    ):
        coluna.metric(
            metrica[0],
            metrica[1]
        )

    aba1, aba2, aba3 = st.tabs(
        [
            "Visão da frente",
            "Atividades",
            "Atualizar",
        ]
    )

    with aba1:

        st.markdown(
            "## Pontos de atenção"
        )

        cards_criticos(
            df,
            7
        )

        st.markdown(
            "## Distribuição"
        )

        grafico_status(
            df
        )

    with aba2:

        c1, c2, c3 = st.columns(3)

        macros = sorted(
            [
                str(v)
                for v
                in df["macroetapa"]
                .dropna()
                .unique()
            ]
        )

        macro = c1.selectbox(
            "Macroetapa",
            ["Todas"] + macros,
            key=f"macro_{frente}",
        )

        status = c2.selectbox(
            "Status",
            ["Todos"] + STATUS,
            key=f"status_{frente}",
        )

        prioridade = c3.selectbox(
            "Prioridade",
            ["Todas"] + PRIORIDADES,
            key=f"prio_{frente}",
        )

        filtrado = df.copy()

        if macro != "Todas":
            filtrado = filtrado[
                filtrado["macroetapa"]
                == macro
            ]

        if status != "Todos":
            filtrado = filtrado[
                filtrado["status"]
                == status
            ]

        if prioridade != "Todas":
            filtrado = filtrado[
                filtrado["prioridade"]
                == prioridade
            ]

        tabela_atividades(
            filtrado
        )

    with aba3:

        st.info(
            "Selecione uma atividade, altere somente "
            "o que for necessário e salve. "
            "A mudança será registrada no D1 e no histórico."
        )

        editor_atividade(
            df,
            frente
        )


# ============================================================
# PESSOAS & ESTRUTURA
# ============================================================

elif pagina == "Pessoas & Estrutura":

    cabecalho(
        "Pessoas & Estrutura",
        "Acompanhamento interno da mobilização de pessoal e estrutura.",
    )

    total = len(
        pessoas
    )

    if pessoas.empty:
        doc = aprovado = integrado = campo = 0
    else:
        doc = int(
            (
                pessoas[
                    "documentacao_enviada"
                ].fillna(0)
                .astype(int)
                == 1
            ).sum()
        )

        aprovado = int(
            (
                pessoas[
                    "aprovado_aqua"
                ].fillna(0)
                .astype(int)
                == 1
            ).sum()
        )

        integrado = int(
            (
                pessoas[
                    "integrado"
                ].fillna(0)
                .astype(int)
                == 1
            ).sum()
        )

        campo = int(
            (
                pessoas[
                    "liberado_campo"
                ].fillna(0)
                .astype(int)
                == 1
            ).sum()
        )

    c = st.columns(5)

    for coluna, metrica in zip(
        c,
        [
            ("Cadastrados", total),
            ("Docs enviados", doc),
            ("Aprovados Aqua", aprovado),
            ("Integrados", integrado),
            ("Liberados campo", campo),
        ],
    ):
        coluna.metric(
            metrica[0],
            metrica[1]
        )

    a1, a2, a3 = st.tabs(
        [
            "Visão quantitativa",
            "Base interna",
            "Atualizar pessoa",
        ]
    )

    with a1:

        if not pessoas.empty:

            linhas = []

            for frente in [
                "Leitura",
                "Cobrança",
                "Hidrometria",
            ]:

                x = pessoas[
                    pessoas["frente"]
                    == frente
                ]

                linhas.append(
                    {
                        "Frente": frente,
                        "Cadastrados":
                            len(x),

                        "Documentação enviada":
                            int(
                                (
                                    x[
                                        "documentacao_enviada"
                                    ]
                                    .fillna(0)
                                    .astype(int)
                                    == 1
                                ).sum()
                            ),

                        "Aprovados Aqua":
                            int(
                                (
                                    x[
                                        "aprovado_aqua"
                                    ]
                                    .fillna(0)
                                    .astype(int)
                                    == 1
                                ).sum()
                            ),

                        "Integrados":
                            int(
                                (
                                    x[
                                        "integrado"
                                    ]
                                    .fillna(0)
                                    .astype(int)
                                    == 1
                                ).sum()
                            ),

                        "Liberados":
                            int(
                                (
                                    x[
                                        "liberado_campo"
                                    ]
                                    .fillna(0)
                                    .astype(int)
                                    == 1
                                ).sum()
                            ),
                    }
                )

            st.dataframe(
                pd.DataFrame(
                    linhas
                ),
                use_container_width=True,
                hide_index=True,
            )

    with a2:

        st.warning(
            "Base nominal de uso interno. "
            "Ela não aparece no Modo Reunião."
        )

        if pessoas.empty:
            st.info(
                "Nenhuma pessoa cadastrada."
            )

        else:
            mostrar = pessoas.copy()

            colunas = [
                "frente",
                "polo_base",
                "nome",
                "funcao",
                "situacao",
                "documentacao_enviada",
                "aprovado_aqua",
                "integrado",
                "liberado_campo",
                "data_admissao",
            ]

            colunas = [
                c
                for c in colunas
                if c in mostrar.columns
            ]

            st.dataframe(
                mostrar[colunas],
                use_container_width=True,
                hide_index=True,
                height=500,
            )

    with a3:

        editor_pessoa()

    st.markdown(
        "## Polos / Bases"
    )

    if polos.empty:
        st.info(
            "Nenhum polo/base cadastrado."
        )

    else:
        st.dataframe(
            polos,
            use_container_width=True,
            hide_index=True,
        )

    if not recursos.empty:

        st.markdown(
            "## Recursos"
        )

        st.dataframe(
            recursos,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# CRONOGRAMA & RAMPAGEM
# ============================================================

elif pagina == "Cronograma & Rampagem":

    cabecalho(
        "Cronograma & Rampagem",
        "Prazos, dependências e evolução da capacidade planejada.",
    )

    a1, a2, a3 = st.tabs(
        [
            "Cronograma",
            "Rampagem",
            "Atualizar rampagem",
        ]
    )

    with a1:

        c1, c2 = st.columns(2)

        frente = c1.selectbox(
            "Frente",
            [
                "Todas",
                "Leitura",
                "Cobrança",
                "Hidrometria",
            ],
            key="cron_frente",
        )

        situacao = c2.selectbox(
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

        x = atividades.copy()

        if frente != "Todas":
            x = x[
                x["frente"]
                == frente
            ]

        if situacao == "Atrasadas":
            x = x[
                x["atrasada"]
            ]

        elif situacao == "Prazo próximo":
            x = x[
                x["prazo_proximo"]
            ]

        elif (
            situacao
            == "Aguardando Aqua"
        ):
            x = x[
                x["status"]
                == "Aguardando Aqua"
            ]

        elif situacao == "Em aberto":
            x = x[
                ~x["status"].isin(
                    [
                        "Concluído",
                        "Cancelado",
                    ]
                )
            ]

        elif situacao == "Concluídas":
            x = x[
                x["status"]
                == "Concluído"
            ]

        tabela_atividades(
            x
        )

    with a2:

        if rampagem.empty:
            st.info(
                "Nenhuma rampagem cadastrada."
            )

        else:
            st.dataframe(
                rampagem,
                use_container_width=True,
                hide_index=True,
            )

            graf = rampagem[
                rampagem["frente"].isin(
                    [
                        "Cobrança",
                        "Hidrometria",
                    ]
                )
            ].copy()

            if not graf.empty:

                fig = go.Figure()

                for frente in [
                    "Cobrança",
                    "Hidrometria",
                ]:

                    x = graf[
                        graf["frente"]
                        == frente
                    ]

                    fig.add_trace(
                        go.Scatter(
                            x=x["periodo"],
                            y=x[
                                "equipes_planejadas"
                            ],
                            mode="lines+markers",
                            name=frente,
                        )
                    )

                fig.update_layout(
                    height=400,
                    paper_bgcolor=(
                        "rgba(0,0,0,0)"
                    ),
                    plot_bgcolor=(
                        "rgba(0,0,0,0)"
                    ),
                    font_color="#dddddf",
                    legend=dict(
                        orientation="h"
                    ),
                    xaxis=dict(
                        gridcolor="#202026"
                    ),
                    yaxis=dict(
                        gridcolor="#202026",
                        title=(
                            "Equipes planejadas"
                        ),
                    ),
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config={
                        "displayModeBar":
                            False
                    },
                )

    with a3:

        editor_rampagem()


# ============================================================
# MODO REUNIÃO
# ============================================================

elif pagina == "Modo Reunião":

    cabecalho(
        "Modo Reunião",
        "Visão executiva para acompanhamento com a Aqua Pernambuco.",
    )

    r = resumo_df(
        atividades
    )

    c = st.columns(4)

    for coluna, metrica in zip(
        c,
        [
            (
                "Dias para Go-Live",
                dias
            ),
            (
                "Mobilização geral",
                f'{r["pct"]:.1f}%'
            ),
            (
                "Concluídos",
                r["concluidos"]
            ),
            (
                "Aguardando Aqua",
                r["aqua"]
            ),
        ],
    ):
        coluna.metric(
            metrica[0],
            metrica[1]
        )

    st.markdown(
        "## Mobilização das frentes"
    )

    for frente in [
        "Leitura",
        "Cobrança",
        "Hidrometria",
    ]:

        z = resumo_df(
            atividades[
                atividades["frente"]
                == frente
            ]
        )

        st.markdown(
            f"**{frente} · "
            f'{z["pct"]:.1f}%**'
        )

        st.progress(
            min(
                z["pct"] / 100,
                1.0
            )
        )

        st.caption(
            f'{z["concluidos"]} de '
            f'{z["total"]} concluídas · '
            f'{z["andamento"]} em andamento · '
            f'{z["aqua"]} aguardando Aqua'
        )

    c1, c2 = st.columns(2)

    with c1:

        st.markdown(
            "## Pontos que exigem ação"
        )

        cards_criticos(
            atividades,
            8
        )

    with c2:

        st.markdown(
            "## Próximos passos"
        )

        x = pontos_criticos(
            atividades,
            8
        )

        for _, linha in x.iterrows():

            acao = (
                txt(
                    linha.get(
                        "proximo_passo_manual"
                    )
                )
                or txt(
                    linha.get(
                        "pendencia_acao"
                    )
                )
            )

            st.markdown(
                f"""
                <div class="piano-card">
                    <div class="piano-title">
                        {
                            txt(
                                linha.get(
                                    "atividade"
                                )
                            )
                        }
                    </div>

                    <div class="piano-body">
                        {
                            acao
                            or
                            "Sem próximo passo registrado."
                        }
                        <br>
                        <b>Responsável:</b>
                        {
                            txt(
                                linha.get(
                                    "responsavel"
                                )
                            )
                            or "—"
                        }
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        "## Pessoas · visão quantitativa"
    )

    if pessoas.empty:
        total_pessoas = 0
        cobranca = 0
        hidro = 0
        leitura = 0
        liberados = 0

    else:
        total_pessoas = len(
            pessoas
        )

        leitura = int(
            (
                pessoas["frente"]
                == "Leitura"
            ).sum()
        )

        cobranca = int(
            (
                pessoas["frente"]
                == "Cobrança"
            ).sum()
        )

        hidro = int(
            (
                pessoas["frente"]
                == "Hidrometria"
            ).sum()
        )

        liberados = int(
            (
                pessoas[
                    "liberado_campo"
                ]
                .fillna(0)
                .astype(int)
                == 1
            ).sum()
        )

    c = st.columns(5)

    for coluna, metrica in zip(
        c,
        [
            (
                "Cadastrados",
                total_pessoas
            ),
            (
                "Leitura",
                leitura
            ),
            (
                "Cobrança",
                cobranca
            ),
            (
                "Hidrometria",
                hidro
            ),
            (
                "Liberados campo",
                liberados
            ),
        ],
    ):
        coluna.metric(
            metrica[0],
            metrica[1]
        )

    st.markdown(
        "## Alterações recentes"
    )

    if historico.empty:

        st.caption(
            "Ainda não existem alterações "
            "registradas no histórico."
        )

    else:

        h = historico.copy()

        if "alterado_em" in h.columns:
            h["alterado_em"] = (
                pd.to_datetime(
                    h["alterado_em"],
                    errors="coerce"
                )
                .dt.strftime(
                    "%d/%m/%Y %H:%M"
                )
            )

        colunas = [
            "tabela",
            "registro_id",
            "campo",
            "valor_anterior",
            "valor_novo",
            "alterado_por",
            "alterado_em",
        ]

        colunas = [
            c
            for c in colunas
            if c in h.columns
        ]

        st.dataframe(
            h[colunas].head(20),
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# RODAPÉ
# ============================================================

st.markdown(
    """
    <div
        class="small-note"
        style="margin-top:40px"
    >
        V0 Black Piano ·
        Aqua Pernambuco – Enorsul ·
        Dados persistidos no Cloudflare D1
    </div>
    """,
    unsafe_allow_html=True,
)
