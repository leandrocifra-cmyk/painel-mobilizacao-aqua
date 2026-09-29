from __future__ import annotations

import io
import json
import hashlib
from pathlib import Path
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk
import streamlit as st

st.set_page_config(page_title="ENORSUL Pernambuco | Mobilização Operacional", page_icon="💧", layout="wide", initial_sidebar_state="collapsed")

APP_DIR = Path(__file__).resolve().parent
DEFAULT_XLSX = APP_DIR / "Base_Aqua_Mobilizacao_FINAL_Validada.xlsx"
OP_SHEETS = ["Cobrança RMR", "Cobrança Interior", "Hidrometria", "Leitura"]
STATUS_ORDER = ["Mobilizada", "Contratada", "Em contratação", "Em recrutamento"]
STATUS_COLORS = {
    "Mobilizada": "#50E36C",
    "Contratada": "#20A9FF",
    "Em contratação": "#FF8A24",
    "Em recrutamento": "#BFC7CF",
}
FRONT_COLORS = {"Leitura": "#20D3E6", "Hidrometria": "#F6C928", "Cobrança": "#FF3947"}
POLO_ORDER = [
    "Recife/RMR", "Carpina", "Vitória de Santo Antão", "Gravatá", "Caruaru",
    "Garanhuns", "Arcoverde", "Afogados da Ingazeira", "Serra Talhada"
]

POLO_ORDER_OPERACIONAL = [
    "Serra Talhada", "Afogados da Ingazeira", "Arcoverde", "Garanhuns",
    "Caruaru", "Gravatá", "Vitória de Santo Antão", "Carpina", "Recife/RMR"
]

POLO_COLORS = {
    "Serra Talhada": "#20A9FF",
    "Afogados da Ingazeira": "#50E36C",
    "Arcoverde": "#F6C928",
    "Garanhuns": "#FF69B4",
    "Caruaru": "#9C5CFF",
    "Gravatá": "#FF8A24",
    "Vitória de Santo Antão": "#20D3E6",
    "Carpina": "#27AE60",
    "Recife/RMR": "#FF3947",
}

def ordem_polos_dinamica(series, base_order=None):
    base_order = base_order or POLO_ORDER_OPERACIONAL
    existentes = [
        str(v).strip()
        for v in series.dropna().astype(str).unique()
        if str(v).strip()
    ]
    conhecidos = [p for p in base_order if p in existentes]
    novos = sorted(p for p in existentes if p not in base_order)
    return conhecidos + novos

CSS = r"""
<style>
:root { --bg:#031522; --panel:#071d2d; --panel2:#09263a; --line:#164c6a; --txt:#f4f8fb; --muted:#9fb4c3; --cyan:#19b9ff; }
.stApp { background: radial-gradient(circle at 50% 0%, #0b2b40 0%, #031522 38%, #020e18 100%); color:var(--txt); }
.block-container { max-width: 1900px; padding: .65rem .8rem 1.4rem; }
header[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility:hidden; }
[data-testid="stToolbar"] { visibility:hidden; }
.hero {display:flex; align-items:center; justify-content:space-between; border-bottom:1px solid #0c4461; padding:4px 8px 14px; margin-bottom:10px;}
.brand {display:flex; align-items:center; gap:24px}.aqua {font-size:34px;font-weight:900;letter-spacing:1px;color:#fff}.aqua span{color:#19b9ff}.sep{height:44px;width:1px;background:#7fa4ba}.title{font-size:26px;font-weight:900;letter-spacing:.8px}.subtitle{font-size:13px;letter-spacing:4px;color:#c7d5df;margin-top:2px}.hero-right{text-align:right;color:#a8bbc8;font-size:11px}.hero-right b{color:#fff;font-size:16px}.logos{font-weight:800;color:#fff;font-size:17px;margin-top:5px}
.panel {background:linear-gradient(180deg,rgba(7,29,45,.96),rgba(4,21,34,.96)); border:1px solid var(--line); border-radius:10px; padding:11px 13px; box-shadow:0 8px 24px rgba(0,0,0,.18);}
.panel-title{font-weight:900;font-size:13px;letter-spacing:.2px;color:#f3f7fa;margin-bottom:7px;text-transform:uppercase}
.kpi {min-height:106px;background:linear-gradient(180deg,#09263a,#061c2c);border:1px solid #1b5270;border-radius:10px;padding:11px 14px;position:relative;overflow:hidden}.kpi-label{font-size:11px;font-weight:800;text-transform:uppercase;color:#dbe7ee;text-align:center}.kpi-value{font-size:34px;font-weight:900;line-height:1.25;color:#fff}.kpi-sub{font-size:12px;color:#b7c9d4}.bar{height:9px;background:#1b3b50;border-radius:4px;margin-top:8px;overflow:hidden}.bar>span{display:block;height:100%;border-radius:4px}.warn{font-size:10px;color:#ffcf66;margin-top:4px}
.filter-title{font-size:11px;font-weight:900;text-transform:uppercase;color:#dbe7ee;margin:1px 0 4px}.small-stat{border:1px solid #174761;border-radius:9px;padding:10px 12px;margin-top:8px;background:#061c2b}.small-stat b{font-size:25px;color:#fff}.small-stat span{font-size:11px;color:#b7c9d4;text-transform:uppercase}
.note{font-size:11px;color:#a8bbc8}.good{color:#50E36C}.blue{color:#20A9FF}.orange{color:#FF8A24}
div[data-testid="stSelectbox"] label, div[data-testid="stMultiSelect"] label {font-size:11px!important;font-weight:800!important;color:#dce8ef!important;text-transform:uppercase}.stSelectbox div[data-baseweb="select"]>div,.stMultiSelect div[data-baseweb="select"]>div{background:#082237;border-color:#174e6d;color:#fff}.stTabs [data-baseweb="tab-list"]{gap:6px}.stTabs [data-baseweb="tab"]{background:#071d2d;border:1px solid #174e6d;border-radius:7px;color:#dce8ef;padding:8px 16px}.stTabs [aria-selected="true"]{background:#0a82c7!important;color:white!important}.stDataFrame{border:1px solid #174e6d;border-radius:8px;overflow:hidden}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def clean_text(s: pd.Series) -> pd.Series:
    return s.fillna("").astype(str).str.strip()


def read_excel_source(source) -> dict[str, pd.DataFrame]:
    xls = pd.ExcelFile(source)
    missing = [s for s in OP_SHEETS + ["Microrrotas", "Bases", "Rampagem"] if s not in xls.sheet_names]
    if missing:
        raise ValueError("Abas obrigatórias ausentes: " + ", ".join(missing))
    data = {name: pd.read_excel(xls, sheet_name=name) for name in xls.sheet_names}
    return data


API_URL_PADRAO = "https://aqua-mobilizacao-api.leandro-cifra.workers.dev"

def api_config():
    api_url = API_URL_PADRAO
    api_key = ""
    try:
        api_url = str(st.secrets.get("API_URL", API_URL_PADRAO)).rstrip("/")
        api_key = str(st.secrets.get("SYNC_API_KEY", "")).strip()
    except Exception:
        pass
    return api_url, api_key

def api_request(path, method="GET", payload=None, timeout=20):
    api_url, api_key = api_config()
    headers = {"Content-Type": "application/json; charset=utf-8"}
    if api_key:
        headers["X-API-Key"] = api_key
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = Request(f"{api_url}{path}", data=body, headers=headers, method=method)
    try:
        with urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except HTTPError as e:
        detalhe = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"API respondeu HTTP {e.code}: {detalhe}") from e
    except URLError as e:
        raise RuntimeError(f"Não foi possível acessar a API: {e.reason}") from e

def valor_json(v):
    if pd.isna(v):
        return None
    if isinstance(v, (pd.Timestamp, datetime)):
        return v.isoformat()
    if hasattr(v, "item"):
        try:
            return v.item()
        except Exception:
            pass
    return v

def dataframes_para_json(data):
    saida = {}
    for nome, df in data.items():
        registros = []
        for row in df.to_dict(orient="records"):
            registros.append({str(k): valor_json(v) for k, v in row.items()})
        saida[nome] = registros
    return saida

def json_para_dataframes(dados):
    return {nome: pd.DataFrame(registros) for nome, registros in dados.items()}

def carregar_ultima_base_api():
    resposta = api_request("/base-operacional/ultima")
    if not resposta.get("ok") or not resposta.get("dados_carga"):
        return None, resposta
    return json_para_dataframes(resposta["dados_carga"]), resposta

def publicar_base_api(upload_bytes, nome_arquivo, data, teams, coverage):
    payload = {
        "nome_arquivo": nome_arquivo,
        "hash_arquivo": hashlib.sha256(upload_bytes).hexdigest(),
        "tamanho_bytes": len(upload_bytes),
        "total_equipes": int(teams["ID Único Equipe / Agente"].nunique()),
        "total_registros": int(len(coverage)),
        "atualizado_por": "Painel ENORSUL Pernambuco",
        "dados_carga": dataframes_para_json(data),
    }
    return api_request("/base-operacional", method="POST", payload=payload, timeout=45)


def build_model(data: dict[str, pd.DataFrame]):
    required = [
        "ID Único Equipe / Agente", "Nome da Equipe", "Nome do Colaborador Líder",
        "Base de Apoio Enorsul", "Município de Origem", "Polo", "Microrrota",
        "Município de Atendimento", "Tipo de Equipe", "Habilidades / Serviços Aptos",
        "Status da Equipe", "Frente Principal", "Veículo Disponível", "Observação"
    ]
    frames = []
    for sh in OP_SHEETS:
        df = data[sh].copy()
        miss = [c for c in required if c not in df.columns]
        if miss:
            raise ValueError(f"Aba '{sh}' sem colunas obrigatórias: {', '.join(miss)}")
        df = df[required].copy()
        df["Aba Origem"] = sh
        frames.append(df)
    coverage = pd.concat(frames, ignore_index=True)
    for c in required:
        coverage[c] = clean_text(coverage[c])
    coverage = coverage[coverage["ID Único Equipe / Agente"] != ""].copy()
    coverage["Região"] = coverage["Polo"].apply(lambda x: "RMR" if x == "Recife/RMR" else "Interior")

    canonical_cols = [
        "ID Único Equipe / Agente", "Nome da Equipe", "Nome do Colaborador Líder",
        "Base de Apoio Enorsul", "Município de Origem", "Tipo de Equipe",
        "Habilidades / Serviços Aptos", "Status da Equipe", "Frente Principal",
        "Veículo Disponível", "Observação"
    ]
    conflicts = []
    for col in canonical_cols[1:]:
        n = coverage.groupby("ID Único Equipe / Agente")[col].nunique(dropna=False)
        bad = n[n > 1]
        for team_id in bad.index:
            vals = sorted(v for v in coverage.loc[coverage["ID Único Equipe / Agente"] == team_id, col].unique() if v)
            conflicts.append({"ID": team_id, "Campo": col, "Valores": " | ".join(vals)})
    teams = coverage.sort_values(["ID Único Equipe / Agente", "Polo", "Microrrota"]).drop_duplicates("ID Único Equipe / Agente")[canonical_cols].copy()

    micro = data["Microrrotas"].copy()
    bases = data["Bases"].copy()
    ramp = data["Rampagem"].copy()
    return teams, coverage, micro, bases, ramp, pd.DataFrame(conflicts)


def options(series):
    vals = sorted(v for v in series.dropna().astype(str).str.strip().unique() if v)
    return vals


def kpi_card(label, value, sub="", pct=None, color="#20A9FF", warn=""):
    pct_html = ""
    if pct is not None:
        pct = max(0, min(100, float(pct)))
        pct_html = f'<div class="bar"><span style="width:{pct:.1f}%;background:{color}"></span></div>'
    warn_html = f'<div class="warn">{warn}</div>' if warn else ""
    st.markdown(f'<div class="kpi"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div><div class="kpi-sub">{sub}</div>{pct_html}{warn_html}</div>', unsafe_allow_html=True)


def panel_title(text):
    st.markdown(f'<div class="panel-title">{text}</div>', unsafe_allow_html=True)


def filter_model(teams, coverage, front, region, polo, micro, status):
    cov = coverage.copy()
    if front != "Todas": cov = cov[cov["Frente Principal"] == front]
    if region != "Todas": cov = cov[cov["Região"] == region]
    if polo != "Todos": cov = cov[cov["Polo"] == polo]
    if micro != "Todas": cov = cov[cov["Microrrota"] == micro]
    ids = set(cov["ID Único Equipe / Agente"])
    t = teams[teams["ID Único Equipe / Agente"].isin(ids)].copy()
    if status != "Todos": t = t[t["Status da Equipe"] == status]
    valid_ids = set(t["ID Único Equipe / Agente"])
    cov = cov[cov["ID Único Equipe / Agente"].isin(valid_ids)].copy()
    return t, cov


def planned_value(ramp, front):
    r = ramp.copy()
    r["Equipes Planejadas"] = pd.to_numeric(r["Equipes Planejadas"], errors="coerce")
    if front != "Todas": r = r[r["Frente"].astype(str).str.strip() == front]
    known = r["Equipes Planejadas"].dropna()
    missing = r["Equipes Planejadas"].isna().any()
    return (int(known.sum()) if len(known) else None), missing


def make_donut(t):
    d = t.groupby("Frente Principal")["ID Único Equipe / Agente"].nunique().reset_index(name="Equipes")
    fig = px.pie(d, values="Equipes", names="Frente Principal", hole=.62, color="Frente Principal", color_discrete_map=FRONT_COLORS)
    fig.update_traces(textinfo="none", hovertemplate="%{label}: %{value}<extra></extra>")
    fig.update_layout(height=245, margin=dict(l=5,r=5,t=5,b=5), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#eaf3f8", legend=dict(orientation="v", y=.5, x=1.0), showlegend=True)
    fig.add_annotation(text=f"<b>{t['ID Único Equipe / Agente'].nunique()}</b><br><span style='font-size:11px'>equipes/agentes</span>", x=.5,y=.5,showarrow=False,font=dict(size=22,color="white"))
    return fig


def make_status(t):
    counts = t["Status da Equipe"].value_counts().reindex(STATUS_ORDER, fill_value=0)
    fig = go.Figure(go.Bar(x=counts.values, y=counts.index, orientation="h", marker_color=[STATUS_COLORS[x] for x in counts.index], text=counts.values, textposition="outside"))
    fig.update_layout(height=245, margin=dict(l=5,r=30,t=5,b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#eaf3f8", xaxis=dict(visible=False), yaxis=dict(autorange="reversed", gridcolor="rgba(255,255,255,.05)"), showlegend=False)
    return fig


def make_ramp_chart(ramp, t):
    r = ramp.copy()
    r["Equipes Planejadas"] = pd.to_numeric(r["Equipes Planejadas"], errors="coerce")
    mobil = t[t["Status da Equipe"] == "Mobilizada"].groupby("Frente Principal")["ID Único Equipe / Agente"].nunique()
    fronts = ["Cobrança", "Hidrometria", "Leitura"]
    fig = go.Figure()
    fig.add_bar(name="Planejado", x=fronts, y=[r.loc[r["Frente"]==f,"Equipes Planejadas"].sum(min_count=1) for f in fronts], marker_color="#5f7585")
    fig.add_bar(name="Mobilizado", x=fronts, y=[mobil.get(f,0) for f in fronts], marker_color=[FRONT_COLORS[f] for f in fronts])
    fig.update_layout(barmode="group", height=260, margin=dict(l=15,r=10,t=10,b=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#eaf3f8", legend=dict(orientation="h", y=1.12), yaxis=dict(gridcolor="rgba(255,255,255,.08)"), xaxis=dict(gridcolor="rgba(0,0,0,0)"))
    return fig


def make_map(micro, bases):
    # Coordenadas operacionais das microrrotas conhecidas.
    # Aplicadas somente no painel: a planilha permanece inalterada.
    # Se a planilha possuir Latitude/Longitude válidas, elas têm prioridade.
    coords_microrrotas = {
        ("Recife/RMR", "MR01"): (-7.7720, -34.9140),
        ("Recife/RMR", "MR02"): (-7.9700, -34.8550),
        ("Recife/RMR", "MR03"): (-8.0400, -35.0100),
        ("Recife/RMR", "MR04"): (-8.2300, -34.9950),
        ("Carpina", "MR01"): (-7.8450, -35.2450),
        ("Carpina", "MR02"): (-7.9900, -35.2900),
        ("Carpina", "MR03"): (-7.7800, -35.5300),
        ("Carpina", "MR04"): (-7.6200, -35.4100),
        ("Carpina", "MR05"): (-7.6200, -35.1000),
        ("Carpina", "MR06"): (-7.5050, -35.3150),
        ("Vitória de Santo Antão", "MR01"): (-8.1600, -35.3150),
        ("Vitória de Santo Antão", "MR02"): (-8.3200, -35.3100),
        ("Vitória de Santo Antão", "MR03"): (-8.8500, -35.1600),
        ("Vitória de Santo Antão", "MR04"): (-8.7100, -35.1700),
        ("Vitória de Santo Antão", "MR05"): (-8.5100, -35.3100),
        ("Gravatá", "MR01"): (-8.4800, -35.6600),
        ("Gravatá", "MR02"): (-8.2050, -35.5650),
        ("Gravatá", "MR03"): (-8.2300, -35.7800),
        ("Gravatá", "MR04"): (-8.4200, -35.8200),
        ("Caruaru", "MR01"): (-8.2840, -35.9700),
        ("Caruaru", "MR02"): (-8.4200, -36.0200),
        ("Caruaru", "MR03"): (-8.6500, -35.9900),
        ("Caruaru", "MR04"): (-8.3500, -36.3500),
        ("Caruaru", "MR05"): (-7.9900, -36.1800),
        ("Caruaru", "MR06"): (-7.9000, -35.9000),
        ("Garanhuns", "MR01"): (-8.8500, -36.5000),
        ("Garanhuns", "MR02"): (-8.9500, -36.3000),
        ("Garanhuns", "MR03"): (-9.0500, -36.6500),
        ("Arcoverde", "MR01"): (-8.6100, -37.1500),
        ("Arcoverde", "MR02"): (-8.3600, -36.8000),
        ("Arcoverde", "MR03"): (-8.8500, -37.3500),
        ("Arcoverde", "MR04"): (-8.2500, -37.3000),
        ("Afogados da Ingazeira", "MR01"): (-7.4200, -37.2500),
        ("Afogados da Ingazeira", "MR02"): (-7.8500, -37.6500),
        ("Afogados da Ingazeira", "MR03"): (-7.7000, -37.5500),
        ("Serra Talhada", "MR01"): (-7.9800, -38.2500),
        ("Serra Talhada", "MR02"): (-8.7500, -38.4500),
        ("Serra Talhada", "MR03"): (-8.3000, -38.9000),
    }

    # Cor territorial por polo.
    # Novas microrrotas de um polo existente herdam automaticamente a mesma cor.
    polo_colors = {
        "Serra Talhada": [32, 169, 255, 210],
        "Afogados da Ingazeira": [80, 227, 108, 210],
        "Arcoverde": [246, 201, 40, 210],
        "Garanhuns": [255, 105, 180, 210],
        "Caruaru": [156, 92, 255, 210],
        "Gravatá": [255, 138, 36, 210],
        "Vitória de Santo Antão": [32, 211, 230, 210],
        "Carpina": [39, 174, 96, 210],
        "Recife/RMR": [255, 57, 71, 210],
    }
    cor_padrao = [191, 199, 207, 210]

    valid = micro.copy()
    if "Latitude" not in valid.columns:
        valid["Latitude"] = pd.NA
    if "Longitude" not in valid.columns:
        valid["Longitude"] = pd.NA

    valid["Latitude"] = pd.to_numeric(valid["Latitude"], errors="coerce")
    valid["Longitude"] = pd.to_numeric(valid["Longitude"], errors="coerce")

    # Coordenadas da planilha têm prioridade.
    # Quando ausentes, usa fallback apenas para as microrrotas já conhecidas.
    for idx, row in valid.iterrows():
        if pd.isna(row["Latitude"]) or pd.isna(row["Longitude"]):
            chave = (
                str(row.get("Polo", "")).strip(),
                str(row.get("Microrrota", "")).strip(),
            )
            coord = coords_microrrotas.get(chave)
            if coord:
                valid.at[idx, "Latitude"] = coord[0]
                valid.at[idx, "Longitude"] = coord[1]

    # A cor depende somente do polo.
    valid["Cor"] = valid["Polo"].apply(
        lambda x: polo_colors.get(str(x).strip(), cor_padrao)
    )

    sem_coordenada = int(
        (valid["Latitude"].isna() | valid["Longitude"].isna()).sum()
    )

    valid = valid[
        valid["Latitude"].notna() & valid["Longitude"].notna()
    ].copy()

    layers = []
    if not valid.empty:
        layers.append(
            pdk.Layer(
                "ScatterplotLayer",
                valid,
                get_position="[Longitude, Latitude]",
                get_radius=9000,
                get_fill_color="Cor",
                pickable=True,
            )
        )

    deck = pdk.Deck(
        map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
        initial_view_state=pdk.ViewState(
            latitude=-8.35,
            longitude=-37.20,
            zoom=6.3,
            pitch=0,
        ),
        layers=layers,
        tooltip={
            "text": "{Polo} • {Microrrota}\n{Municípios de Atendimento}"
        } if layers else None,
    )
    return deck, len(valid), sem_coordenada


def main():
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    st.markdown(f"""<div class="hero"><div class="brand"><div class="aqua">ENORSUL - <span>PERNAMBUCO</span></div><div class="sep"></div><div><div class="title">MOBILIZAÇÃO OPERACIONAL</div><div class="subtitle">LEITURA | HIDROMETRIA | COBRANÇA</div></div></div><div class="hero-right">ÚLTIMA ATUALIZAÇÃO<br><b>{now}</b></div></div>""", unsafe_allow_html=True)

    upload = None
    publicar = False
    with st.expander("⚙️ Administração / Atualizar base", expanded=False):
        st.caption("Carregue a planilha oficial, valide os dados e publique no banco central. Após a publicação, a base fica disponível para todas as sessões do painel.")
        upload = st.file_uploader("Planilha ENORSUL Pernambuco (.xlsx)", type=["xlsx"])
        st.info("Regra estrutural: efetivo = ID Único Equipe / Agente. Linhas repetidas preservam cobertura territorial e não duplicam o KPI.")
        if upload:
            publicar = st.button("Publicar esta base", type="primary", use_container_width=True)

    origem_base = "Base local de contingência"
    api_meta = None
    upload_bytes = upload.getvalue() if upload else None

    try:
        if upload_bytes:
            data = read_excel_source(io.BytesIO(upload_bytes))
            origem_base = f"Pré-visualização: {upload.name}"
        else:
            try:
                data_api, api_meta = carregar_ultima_base_api()
            except Exception:
                data_api, api_meta = None, None
            if data_api is not None:
                data = data_api
                origem_base = f"Base publicada no D1 • versão {api_meta.get('versao', '—')}"
            else:
                if not DEFAULT_XLSX.exists():
                    st.error("Nenhuma base publicada foi encontrada na API e a base local de contingência não existe.")
                    st.stop()
                data = read_excel_source(DEFAULT_XLSX)

        teams, coverage, micro_df, bases_df, ramp_df, conflicts = build_model(data)
    except Exception as e:
        st.error(f"Não foi possível carregar a base: {e}")
        st.stop()

    if publicar and upload_bytes:
        try:
            with st.spinner("Publicando a base no D1..."):
                resposta = publicar_base_api(upload_bytes, upload.name, data, teams, coverage)
            if resposta.get("ok"):
                st.success(f"Base publicada com sucesso. Versão {resposta.get('versao', '—')} • {resposta.get('total_equipes', 0)} equipes/agentes únicos • {resposta.get('total_registros', 0)} vínculos territoriais.")
                origem_base = f"Base publicada no D1 • versão {resposta.get('versao', '—')}"
            else:
                st.error(f"A API recusou a publicação: {resposta}")
        except Exception as e:
            st.error(f"Falha ao publicar no D1: {e}")

    st.caption(f"Fonte atual: {origem_base}")

    left, main_area = st.columns([1.15, 8.85], gap="small")
    with left:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        panel_title("Filtros")
        front = st.selectbox("Frente", ["Todas"] + options(coverage["Frente Principal"]), index=0)
        region = st.selectbox("Região", ["Todas", "RMR", "Interior"], index=0)
        cov_for_polo = coverage.copy()
        if front != "Todas": cov_for_polo = cov_for_polo[cov_for_polo["Frente Principal"] == front]
        if region != "Todas": cov_for_polo = cov_for_polo[cov_for_polo["Região"] == region]
        polo = st.selectbox("Polo", ["Todos"] + options(cov_for_polo["Polo"]), index=0)
        cov_for_micro = cov_for_polo if polo == "Todos" else cov_for_polo[cov_for_polo["Polo"] == polo]
        micro = st.selectbox("Microrrota", ["Todas"] + options(cov_for_micro["Microrrota"]), index=0)
        status = st.selectbox("Status", ["Todos"] + STATUS_ORDER, index=0)
        st.markdown('</div>', unsafe_allow_html=True)

        t, cov = filter_model(teams, coverage, front, region, polo, micro, status)
        municipalities = cov["Município de Atendimento"].replace("", pd.NA).nunique()
        micros = cov[["Polo","Microrrota"]].drop_duplicates().shape[0]
        poles = cov["Polo"].replace("", pd.NA).nunique()
        st.markdown(f'<div class="small-stat"><span>Municípios cobertos</span><br><b>{municipalities}</b></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="small-stat"><span>Microrrotas</span><br><b>{micros}</b></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="small-stat"><span>Polos</span><br><b>{poles}</b></div>', unsafe_allow_html=True)

    with main_area:
        t, cov = filter_model(teams, coverage, front, region, polo, micro, status)
        total = t["ID Único Equipe / Agente"].nunique()
        counts = t["Status da Equipe"].value_counts()
        planned, missing_plan = planned_value(ramp_df, front)
        mobil = int(counts.get("Mobilizada",0)); contrat = int(counts.get("Contratada",0)); hiring = int(counts.get("Em contratação",0)); recruit = int(counts.get("Em recrutamento",0))
        vehicles = t.loc[t["Veículo Disponível"].str.casefold()=="sim", "ID Único Equipe / Agente"].nunique()
        denom = planned if planned and front != "Todas" else total

        kcols = st.columns(6, gap="small")
        with kcols[0]: kpi_card("Equipes planejadas", "—" if planned is None else planned, "meta da aba Rampagem", warn="Meta parcial: há frente sem valor oficial" if missing_plan else "")
        with kcols[1]: kpi_card("Mobilizadas", mobil, f"{(mobil/denom*100 if denom else 0):.0f}%", (mobil/denom*100 if denom else 0), STATUS_COLORS["Mobilizada"])
        with kcols[2]: kpi_card("Contratadas", contrat, f"{(contrat/denom*100 if denom else 0):.0f}%", (contrat/denom*100 if denom else 0), STATUS_COLORS["Contratada"])
        with kcols[3]: kpi_card("Em contratação", hiring, f"{(hiring/denom*100 if denom else 0):.0f}%", (hiring/denom*100 if denom else 0), STATUS_COLORS["Em contratação"])
        with kcols[4]: kpi_card("Em recrutamento", recruit, f"{(recruit/denom*100 if denom else 0):.0f}%", (recruit/denom*100 if denom else 0), STATUS_COLORS["Em recrutamento"])
        with kcols[5]: kpi_card("Veículos disponíveis", vehicles, f"{(vehicles/total*100 if total else 0):.0f}% do efetivo", (vehicles/total*100 if total else 0), "#20A9FF")

        map_col, right_col = st.columns([7.2, 2.8], gap="small")
        with map_col:
            st.markdown('<div class="panel">', unsafe_allow_html=True); panel_title("Mapa de Pernambuco • Mobilização territorial")
            deck, valid_coords, sem_coordenada = make_map(micro_df, bases_df)
            st.pydeck_chart(deck, use_container_width=True, height=500)
            if valid_coords == 0:
                st.caption("Nenhuma microrrota possui coordenadas disponíveis para exibição no mapa.")
            elif sem_coordenada:
                st.caption(f"{sem_coordenada} microrrota(s) sem coordenadas não foi(ram) exibida(s) no mapa.")
            st.markdown('</div>', unsafe_allow_html=True)
        with right_col:
            st.markdown('<div class="panel">', unsafe_allow_html=True); panel_title("Distribuição por frente")
            st.plotly_chart(make_donut(t), use_container_width=True, config={"displayModeBar":False})
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="panel" style="margin-top:8px">', unsafe_allow_html=True); panel_title("Status das equipes")
            st.plotly_chart(make_status(t), use_container_width=True, config={"displayModeBar":False})
            st.markdown('</div>', unsafe_allow_html=True)

        lower1, lower2 = st.columns([5.6,4.4], gap="small")
        with lower1:
            st.markdown('<div class="panel">', unsafe_allow_html=True); panel_title("Mobilização por polo")
            p = cov[["ID Único Equipe / Agente", "Polo"]].drop_duplicates().merge(
                t[["ID Único Equipe / Agente", "Status da Equipe"]],
                on="ID Único Equipe / Agente",
                how="inner",
            )
            pt = (
                p.groupby(["Polo", "Status da Equipe"])["ID Único Equipe / Agente"]
                .nunique()
                .reset_index(name="Equipes")
            )
            polos_grafico = ordem_polos_dinamica(pt["Polo"])
            totais_polo = (
                p.groupby("Polo")["ID Único Equipe / Agente"]
                .nunique()
                .reindex(polos_grafico)
                .fillna(0)
                .astype(int)
            )

            figp = px.bar(
                pt,
                x="Polo",
                y="Equipes",
                color="Status da Equipe",
                category_orders={
                    "Polo": polos_grafico,
                    "Status da Equipe": STATUS_ORDER,
                },
                color_discrete_map=STATUS_COLORS,
            )

            for polo_nome, total_polo in totais_polo.items():
                figp.add_annotation(
                    x=polo_nome,
                    y=total_polo,
                    text=f"<b>{total_polo}</b>",
                    showarrow=False,
                    yshift=10,
                    font=dict(size=11, color="#FFFFFF"),
                )

            figp.update_layout(
                height=300,
                barmode="stack",
                margin=dict(l=10, r=10, t=34, b=65),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#eaf3f8",
                legend=dict(
                    orientation="h",
                    y=1.18,
                    x=0,
                    font=dict(size=10),
                ),
                yaxis=dict(
                    title=None,
                    gridcolor="rgba(255,255,255,.08)",
                    rangemode="tozero",
                ),
                xaxis=dict(
                    title=None,
                    tickangle=-18,
                    tickfont=dict(size=10),
                    categoryorder="array",
                    categoryarray=polos_grafico,
                ),
            )
            st.plotly_chart(
                figp,
                use_container_width=True,
                config={"displayModeBar": False},
            )
            st.markdown('</div>', unsafe_allow_html=True)
        with lower2:
            st.markdown('<div class="panel">', unsafe_allow_html=True); panel_title("Planejado × mobilizado")
            st.plotly_chart(make_ramp_chart(ramp_df, t), use_container_width=True, config={"displayModeBar":False})
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="panel" style="margin-top:8px">', unsafe_allow_html=True); panel_title("Microrrotas por polo")
        polos_micro = ordem_polos_dinamica(micro_df["Polo"])
        mm = (
            micro_df.groupby("Polo")["Microrrota"]
            .nunique()
            .reindex(polos_micro)
            .dropna()
            .astype(int)
        )
        if len(mm):
            cols = st.columns(len(mm), gap="small")
            for col, (name, val) in zip(cols, mm.items()):
                cor_polo = POLO_COLORS.get(name, "#BFC7CF")
                with col:
                    st.markdown(
                        f"<div style='text-align:center'>"
                        f"<div style='font-size:10px;color:#b9cbd6;min-height:28px'>{name}</div>"
                        f"<div style='font-size:23px;font-weight:900;color:#fff'>{val}</div>"
                        f"<div style='height:6px;border-radius:4px;background:{cor_polo};margin-top:5px'></div>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
        st.markdown('</div>', unsafe_allow_html=True)

        tabs = st.tabs(["Detalhamento / Auditoria", "Bases operacionais", "Qualidade da base"])
        with tabs[0]:
            detail_cols = ["ID Único Equipe / Agente","Nome da Equipe","Nome do Colaborador Líder","Frente Principal","Status da Equipe","Polo","Microrrota","Município de Atendimento","Tipo de Equipe","Veículo Disponível","Base de Apoio Enorsul","Habilidades / Serviços Aptos","Observação"]
            st.dataframe(cov[detail_cols].sort_values(["Frente Principal","Polo","Microrrota","ID Único Equipe / Agente"]), use_container_width=True, hide_index=True, height=420)
            st.caption(f"{t['ID Único Equipe / Agente'].nunique()} IDs únicos • {len(cov)} vínculos territoriais no filtro atual.")
        with tabs[1]:
            b = bases_df.copy()
            if front != "Todas" and "Frente" in b: b = b[b["Frente"].astype(str).str.strip()==front]
            if polo != "Todos" and "Base / Polo" in b: b = b[b["Base / Polo"].astype(str).str.strip()==polo]
            st.dataframe(b, use_container_width=True, hide_index=True, height=350)
        with tabs[2]:
            q1,q2,q3,q4 = st.columns(4)
            q1.metric("IDs únicos", teams["ID Único Equipe / Agente"].nunique())
            q2.metric("Vínculos territoriais", len(coverage))
            q3.metric("Conflitos em ID", conflicts["ID"].nunique() if not conflicts.empty else 0)
            q4.metric("Microrrotas cadastradas", micro_df[["Polo","Microrrota"]].drop_duplicates().shape[0])
            if conflicts.empty:
                st.success("Nenhum conflito encontrado nos campos principais de IDs repetidos.")
            else:
                st.warning("Há IDs repetidos com dados principais divergentes. Revise antes de publicar a base.")
                st.dataframe(conflicts, use_container_width=True, hide_index=True)
            fict = coverage[coverage["Observação"].str.contains("FICTÍCIO", case=False, na=False)]
            if len(fict):
                st.warning(f"A base atual contém {len(fict)} linhas marcadas como dado fictício/teste. O painel está apto para teste, mas esses registros não devem ser tratados como produção.")

if __name__ == "__main__":
    main()
