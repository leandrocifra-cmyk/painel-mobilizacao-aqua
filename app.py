import streamlit as st
import pandas as pd
import requests
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

API_URL = "https://aqua-mobilizacao-api.leandro-cifra.workers.dev"
GO_LIVE = date(2026, 10, 26)

STATUS_VALIDOS = [
    "Não iniciado",
    "Em andamento",
    "Aguardando Aqua",
    "Concluído",
    "Cancelado",
]

STATUS_CORES = {
    "Não iniciado": "#667085",
    "Aguardando Aqua": "#2F80ED",
    "Concluído": "#39FF88",
    "Em andamento": "#FFB020",
    "Cancelado": "#475467",
}

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

        .stApp {
            background: #07090D;
            color: #F5F7FA;
        }

        [data-testid="stSidebar"] {
            background: #0B0E14;
        }

        [data-testid="stMetric"] {
            background: rgba(255,255,255,0.045) !important;
            border: 1px solid rgba(255,255,255,0.08) !important;
            box-shadow: 0 10px 30px rgba(0,0,0,.18);
        }

        .card {
            background: rgba(255,255,255,0.045) !important;
            border: 1px solid rgba(255,255,255,0.08) !important;
            box-shadow: 0 10px 30px rgba(0,0,0,.16);
        }

        .macro-card {
            background: rgba(255,255,255,0.045);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 16px;
            padding: 15px 16px 13px 16px;
            min-height: 138px;
            box-shadow: 0 10px 30px rgba(0,0,0,.16);
        }
        .macro-label { color:#AAB2C0; font-size:.80rem; font-weight:650; }
        .macro-value { color:#F8FAFC; font-size:1.65rem; font-weight:800; margin:2px 0 8px 0; }
        .macro-sub { color:#98A2B3; font-size:.76rem; margin-top:7px; }
        .progress-track { height:8px; background:#20242D; border-radius:999px; overflow:hidden; }
        .progress-fill { height:100%; border-radius:999px; box-shadow:0 0 12px rgba(57,255,136,.22); }
        .status-dot { display:inline-block; width:9px; height:9px; border-radius:50%; margin-right:7px; box-shadow:0 0 10px currentColor; }
        .alerta-atraso {
            display:inline-flex; align-items:center; gap:6px;
            color:#FF4D6D; font-weight:750; font-size:.76rem;
            text-shadow:0 0 10px rgba(255,77,109,.45);
        }
        .section-shell {
            background: rgba(255,255,255,0.025);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 18px;
            padding: 12px 14px 4px 14px;
            margin: 8px 0 14px 0;
        }

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


def percentual_seguro(parte, total):
    total = numero(total)
    parte = numero(parte)
    if total <= 0:
        return 0.0
    return max(0.0, min(100.0, parte / total * 100))


def recursos_por_categoria(termos):
    if df_recursos.empty:
        return 0, 0
    base = df_recursos.copy()
    for campo in ["categoria", "descricao"]:
        if campo not in base.columns:
            base[campo] = ""
    texto_busca = (base["categoria"].fillna("").astype(str) + " " + base["descricao"].fillna("").astype(str)).str.lower()
    mascara = False
    for termo in termos:
        mascara = mascara | texto_busca.str.contains(termo.lower(), regex=False)
    base = base[mascara].copy()
    if base.empty:
        return 0, 0
    planejado = pd.to_numeric(base.get("quantidade_planejada", 0), errors="coerce").fillna(0).sum()
    disponivel = pd.to_numeric(base.get("quantidade_disponivel", 0), errors="coerce").fillna(0).sum()
    return int(planejado), int(disponivel)


def indicadores_mobilizacao_macro():
    total_pessoas = len(df_pessoas)
    aprovados = 0
    docs = 0
    if not df_pessoas.empty:
        if "aprovado_aqua" in df_pessoas.columns:
            aprovados = int(pd.to_numeric(df_pessoas["aprovado_aqua"], errors="coerce").fillna(0).sum())
        if "documentacao_enviada" in df_pessoas.columns:
            docs = int(pd.to_numeric(df_pessoas["documentacao_enviada"], errors="coerce").fillna(0).sum())
    frota_plan, frota_disp = recursos_por_categoria(["frota", "veículo", "veiculo", "carro", "moto"])
    epi_plan, epi_disp = recursos_por_categoria(["epi", "fardamento", "uniforme", "bota", "camisa", "calça", "calca"])
    return [
        ("Contratação de pessoal", percentual_seguro(aprovados, total_pessoas), f"{aprovados} aprovados de {total_pessoas}"),
        ("Frota", percentual_seguro(frota_disp, frota_plan), f"{frota_disp} disponíveis de {frota_plan}"),
        ("Documentação", percentual_seguro(docs, total_pessoas), f"{docs} completos de {total_pessoas}"),
        ("Fardamento & EPI", percentual_seguro(epi_disp, epi_plan), f"{epi_disp} disponíveis de {epi_plan}"),
    ]


def card_macro(titulo, pct, detalhe):
    if pct >= 100:
        cor = STATUS_CORES["Concluído"]
    elif pct > 0:
        cor = STATUS_CORES["Em andamento"]
    else:
        cor = STATUS_CORES["Não iniciado"]
    st.markdown(
        f"""<div class='macro-card'>
        <div class='macro-label'>{titulo}</div>
        <div class='macro-value'>{pct:.0f}%</div>
        <div class='progress-track'><div class='progress-fill' style='width:{pct:.1f}%;background:{cor};'></div></div>
        <div class='macro-sub'>{detalhe}</div>
        </div>""", unsafe_allow_html=True
    )


def salvar_atividade_api(atividade_id, payload):
    erros = []
    for metodo in ("patch", "put"):
        try:
            fn = getattr(requests, metodo)
            r = fn(f"{API_URL}/atividades/{atividade_id}", json=payload, timeout=20)
            if r.ok:
                st.cache_data.clear()
                return True, None
            erros.append(f"{metodo.upper()}: HTTP {r.status_code}")
        except Exception as exc:
            erros.append(f"{metodo.upper()}: {exc}")
    return False, " | ".join(erros)


def editor_atividade(base, chave):
    if base.empty or "id" not in base.columns:
        return
    st.markdown("### Atualização rápida")
    opcoes = base.dropna(subset=["id"]).copy()
    if opcoes.empty:
        st.caption("Nenhuma atividade com ID disponível para edição.")
        return
    rotulos = {str(r["id"]): f"{texto(r.get('macroetapa'),'')} · {texto(r.get('atividade'))}" for _, r in opcoes.iterrows()}
    atividade_id = st.selectbox("Atividade para editar", list(rotulos.keys()), format_func=lambda x: rotulos[x], key=f"edit_id_{chave}")
    row = opcoes[opcoes["id"].astype(str) == str(atividade_id)].iloc[0]
    c1, c2, c3 = st.columns([1.1, .7, 1.2])
    status_atual = texto(row.get("status"), "Não iniciado")
    idx = STATUS_VALIDOS.index(status_atual) if status_atual in STATUS_VALIDOS else 0
    novo_status = c1.selectbox("Status", STATUS_VALIDOS, index=idx, key=f"edit_status_{chave}")
    novo_pct = c2.number_input("%", min_value=0, max_value=100, value=numero(row.get("percentual")), step=5, key=f"edit_pct_{chave}")
    novo_resp = c3.text_input("Responsável", value=texto(row.get("responsavel"), ""), key=f"edit_resp_{chave}")
    novo_passo = st.text_area("Próximo passo / pendência", value=texto(row.get("pendencia_acao"), ""), height=80, key=f"edit_passo_{chave}")
    if st.button("Salvar alteração", type="primary", key=f"save_{chave}"):
        payload = {"status": novo_status, "percentual": int(novo_pct), "responsavel": novo_resp, "pendencia_acao": novo_passo}
        ok, erro = salvar_atividade_api(atividade_id, payload)
        if ok:
            st.success("Alteração salva na base.")
            st.rerun()
        else:
            st.error("A tela de edição está pronta, mas a API ainda não aceitou gravação. É necessário habilitar PATCH/PUT no Worker. " + (erro or ""))


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


def pagina_frente(nome_frente):
    cabecalho(
        nome_frente,
        f"Acompanhamento da mobilização da frente de {nome_frente.lower()}.",
    )

    indicadores_frente(nome_frente)

    if df_atividades.empty:
        st.info("Não há atividades disponíveis.")
        return

    base = df_atividades[
        df_atividades["frente"] == nome_frente
    ].copy()

    st.markdown("## Pontos de atenção")

    criticos = pontos_criticos(base, 6)

    if criticos.empty:
        st.success("Nenhum ponto crítico identificado nesta frente.")
    else:
        for _, row in criticos.iterrows():
            prazo = data_br(row.get("data_prevista"))

            marcadores = []

            if bool(row.get("atrasada")):
                marcadores.append("ATRASADA")

            if row.get("status") == "Aguardando Aqua":
                marcadores.append("AGUARDANDO AQUA")

            if bool(row.get("prazo_proximo")):
                marcadores.append("PRAZO PRÓXIMO")

            if texto(row.get("prioridade"), ""):
                marcadores.append(texto(row.get("prioridade")))

            tags = " ".join(
                [f"<span class='tag' style='color:{STATUS_CORES.get('Em andamento','#FFB020') if x != 'ATRASADA' else '#FF4D6D'}'>{'● ' if x == 'ATRASADA' else ''}{x}</span>" for x in marcadores]
            )

            st.markdown(
                f"""
                <div class="card">
                    <div class="card-titulo">
                        {texto(row.get("atividade"))}
                    </div>
                    <div>{tags}</div>
                    <div class="card-texto">
                        <b>Responsável:</b> {texto(row.get("responsavel"))}
                        &nbsp;&nbsp;|&nbsp;&nbsp;
                        <b>Prazo:</b> {prazo}<br>
                        <b>Próximo passo:</b> {proximo_passo(row)}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("## Atividades")

    macroetapas = sorted(
        [
            x
            for x in base["macroetapa"].dropna().unique().tolist()
            if str(x).strip()
        ]
    )

    f1, f2, f3 = st.columns([1.4, 1.2, 1.2])

    macro = f1.selectbox(
        "Macroetapa",
        ["Todas"] + macroetapas,
        key=f"macro_{nome_frente}",
    )

    status = f2.selectbox(
        "Status",
        ["Todos"] + STATUS_VALIDOS,
        key=f"status_{nome_frente}",
    )

    prioridade = f3.selectbox(
        "Prioridade",
        ["Todas", "Crítica", "Alta", "Média", "Baixa"],
        key=f"prioridade_{nome_frente}",
    )

    filtrado = base.copy()

    if macro != "Todas":
        filtrado = filtrado[filtrado["macroetapa"] == macro]

    if status != "Todos":
        filtrado = filtrado[filtrado["status"] == status]

    if prioridade != "Todas":
        filtrado = filtrado[filtrado["prioridade"] == prioridade]

    tabela_atividades(filtrado)

    with st.expander("✏️ Editar atividade diretamente no painel", expanded=False):
        editor_atividade(base, nome_frente)

    st.markdown("## Critério de aceite e evidências")

    detalhes = base[
        [
            "atividade",
            "criterio_aceite",
            "evidencia",
            "observacao",
        ]
    ].copy()

    detalhes = detalhes.rename(
        columns={
            "atividade": "Atividade",
            "criterio_aceite": "Critério de aceite",
            "evidencia": "Evidência",
            "observacao": "Observação",
        }
    )

    st.dataframe(
        detalhes,
        use_container_width=True,
        hide_index=True,
        height=330,
    )


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

    st.markdown("## Mobilização operacional")
    m1, m2, m3, m4 = st.columns(4)
    macros = indicadores_mobilizacao_macro()
    for coluna, item in zip([m1, m2, m3, m4], macros):
        with coluna:
            card_macro(*item)

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

    st.markdown("## Indicadores macro de mobilização")
    g1, g2, g3, g4 = st.columns(4)
    macros = indicadores_mobilizacao_macro()
    for coluna, item in zip([g1, g2, g3, g4], macros):
        with coluna:
            card_macro(*item)

    tab1, tab2, tab3 = st.tabs(
        ["Pessoas", "Polos e Bases", "Recursos"]
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

# ============================================================
# 6. CRONOGRAMA & RAMPAGEM
# ============================================================

elif pagina == "Cronograma & Rampagem":
    cabecalho(
        "Cronograma & Rampagem",
        "Prazos da implantação e evolução planejada versus mobilizada.",
    )

    tab1, tab2 = st.tabs(["Cronograma", "Rampagem"])

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
        V1 — layout executivo + edição direta ·
        Dados carregados da base estruturada de mobilização ·
        Go-Live: 26/10/2026
    </div>
    """,
    unsafe_allow_html=True,
)
