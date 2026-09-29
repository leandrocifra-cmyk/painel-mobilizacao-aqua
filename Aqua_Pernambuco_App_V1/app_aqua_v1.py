from __future__ import annotations

import io
from pathlib import Path
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk
import streamlit as st

st.set_page_config(page_title="Aqua Pernambuco | Mobilização Operacional", page_icon="💧", layout="wide", initial_sidebar_state="collapsed")

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

CSS = r"""
<style>
:root { --bg:#031522; --panel:#071d2d; --panel2:#09263a; --line:#164c6a; --txt:#f4f8fb; --muted:#9fb4c3; --cyan:#19b9ff; }
.stApp { background: radial-gradient(circle at 50% 0%, #0b2b40 0%, #031522 38%, #020e18 100%); color:var(--txt); }
.block-container { max-width: 1900px; padding: .65rem .8rem 1.4rem; }
header[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility:hidden; }
[data-testid="stToolbar"] { visibility:hidden; }
.hero {display:flex; align-items:center; justify-content:space-between; border-bottom:1px solid #0c4461; padding:4px 8px 14px; margin-bottom:10px;}
.brand {display:flex; align-items:center; gap:24px}.aqua {font-size:28px;font-weight:900;white-space:nowrap;letter-spacing:1px;color:#fff}.aqua span{color:#19b9ff}.sep{height:44px;width:1px;background:#7fa4ba}.title{font-size:26px;font-weight:900;letter-spacing:.8px}.subtitle{font-size:13px;letter-spacing:4px;color:#c7d5df;margin-top:2px}.hero-right{text-align:right;color:#a8bbc8;font-size:11px}.hero-right b{color:#fff;font-size:16px}.logos{font-weight:800;color:#fff;font-size:17px;margin-top:5px}
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
    # Regra: sem coordenadas oficiais, nenhum marcador é inventado.
    lat = pd.to_numeric(micro.get("Latitude", pd.Series(dtype=float)), errors="coerce")
    lon = pd.to_numeric(micro.get("Longitude", pd.Series(dtype=float)), errors="coerce")
    valid = micro[lat.notna() & lon.notna()].copy() if len(micro) else pd.DataFrame()
    layers = []
    if not valid.empty:
        valid["Latitude"] = pd.to_numeric(valid["Latitude"], errors="coerce")
        valid["Longitude"] = pd.to_numeric(valid["Longitude"], errors="coerce")
        layers.append(pdk.Layer("ScatterplotLayer", valid, get_position="[Longitude, Latitude]", get_radius=9000, get_fill_color=[25,185,255,180], pickable=True))
    deck = pdk.Deck(
        map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
        initial_view_state=pdk.ViewState(latitude=-8.35, longitude=-37.75, zoom=6.0, pitch=0),
        layers=layers,
        tooltip={"text":"{Polo} • {Microrrota}"} if layers else None,
    )
    return deck, len(valid)


def main():
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    st.markdown(f"""<div class="hero"><div class="brand"><div class="aqua">ENORSUL - <span>PERNAMBUCO</span></div><div class="sep"></div><div><div class="title">MOBILIZAÇÃO OPERACIONAL</div><div class="subtitle">LEITURA | HIDROMETRIA | COBRANÇA</div></div></div><div class="hero-right">ÚLTIMA ATUALIZAÇÃO<br><b>{now}</b><div class="logos">Enorsul &nbsp; | &nbsp; A serviço da VITA Sertão</div></div></div>""", unsafe_allow_html=True)

    with st.expander("⚙️ Administração / Atualizar base", expanded=False):
        st.caption("Carregue uma nova versão da planilha oficial. A atualização vale para esta sessão; a persistência em API/D1 entra na etapa de publicação.")
        upload = st.file_uploader("Planilha Aqua Pernambuco (.xlsx)", type=["xlsx"])
        st.info("Regra estrutural: efetivo = ID Único Equipe / Agente. Linhas repetidas preservam cobertura territorial e não duplicam o KPI.")

    source = io.BytesIO(upload.getvalue()) if upload else DEFAULT_XLSX
    if not upload and not DEFAULT_XLSX.exists():
        st.error("Base padrão não encontrada ao lado do app. Carregue a planilha no bloco Administração.")
        st.stop()
    try:
        data = read_excel_source(source)
        teams, coverage, micro_df, bases_df, ramp_df, conflicts = build_model(data)
    except Exception as e:
        st.error(f"Não foi possível carregar a base: {e}")
        st.stop()

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
            deck, valid_coords = make_map(micro_df, bases_df)
            st.pydeck_chart(deck, use_container_width=True, height=500)
            if valid_coords == 0:
                st.caption("Coordenadas oficiais ainda não preenchidas. O mapa permanece sem marcadores para não criar posições aproximadas.")
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
            p = cov[["ID Único Equipe / Agente","Polo"]].drop_duplicates().merge(t[["ID Único Equipe / Agente","Status da Equipe"]], on="ID Único Equipe / Agente", how="inner")
            pt = p.groupby(["Polo","Status da Equipe"])["ID Único Equipe / Agente"].nunique().reset_index(name="Equipes")
            figp = px.bar(pt, x="Polo", y="Equipes", color="Status da Equipe", category_orders={"Polo":POLO_ORDER,"Status da Equipe":STATUS_ORDER}, color_discrete_map=STATUS_COLORS)
            figp.update_layout(height=270, barmode="stack", margin=dict(l=10,r=10,t=5,b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#eaf3f8", legend=dict(orientation="h", y=1.16), yaxis=dict(gridcolor="rgba(255,255,255,.08)"), xaxis_tickangle=-25)
            st.plotly_chart(figp, use_container_width=True, config={"displayModeBar":False})
            st.markdown('</div>', unsafe_allow_html=True)
        with lower2:
            st.markdown('<div class="panel">', unsafe_allow_html=True); panel_title("Planejado × mobilizado")
            st.plotly_chart(make_ramp_chart(ramp_df, t), use_container_width=True, config={"displayModeBar":False})
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="panel" style="margin-top:8px">', unsafe_allow_html=True); panel_title("Microrrotas por polo")
        mm = micro_df.groupby("Polo")["Microrrota"].nunique().reindex(POLO_ORDER).dropna().astype(int)
        cols = st.columns(len(mm), gap="small")
        for col,(name,val) in zip(cols, mm.items()):
            with col:
                st.markdown(f"<div style='text-align:center'><div style='font-size:10px;color:#b9cbd6;min-height:28px'>{name}</div><div style='font-size:23px;font-weight:900;color:#fff'>{val}</div><div style='height:6px;border-radius:4px;background:#19b9ff;margin-top:5px'></div></div>", unsafe_allow_html=True)
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
