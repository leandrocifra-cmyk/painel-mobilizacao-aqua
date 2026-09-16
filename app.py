import io
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title='Mobilização Aqua | Enorsul', page_icon='📊', layout='wide')

GO_LIVE = date(2026, 10, 26)
DEFAULT_FILE = Path(__file__).with_name('Checklist_Mobilizacao_Contratos_ATUALIZADO_16-09_REVISAO_GERAL.xlsx')
FRONTES = ['Leitura', 'Cobrança', 'Hidrometria']
STATUS_ORDER = ['Concluído', 'Em andamento', 'Aguardando Aqua', 'Não iniciado']

st.markdown('''
<style>
.block-container {padding-top: 1.2rem; padding-bottom: 2rem;}
[data-testid="stMetric"] {background:#f7f9fc;border:1px solid #e4e9f0;padding:14px;border-radius:10px;}
.main-title {background:#0b3b78;color:white;padding:18px 22px;border-radius:10px;margin-bottom:14px;}
.main-title h1 {margin:0;font-size:28px}.main-title p {margin:4px 0 0 0;opacity:.9}
.small-note {color:#5f6b7a;font-size:13px}
</style>
''', unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def load_book(file_bytes: bytes):
    xls = pd.ExcelFile(io.BytesIO(file_bytes))
    sheets = {name: pd.read_excel(xls, sheet_name=name) for name in xls.sheet_names}
    return sheets

def get_bytes():
    up = st.sidebar.file_uploader('Atualizar base (.xlsx)', type=['xlsx'])
    if up:
        return up.getvalue(), up.name
    if DEFAULT_FILE.exists():
        return DEFAULT_FILE.read_bytes(), DEFAULT_FILE.name
    return None, None

def normalize_front(df):
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df

file_bytes, source_name = get_bytes()
if not file_bytes:
    st.error('Inclua a planilha de mobilização para iniciar.')
    st.stop()

sheets = load_book(file_bytes)
fronts = {f: normalize_front(sheets[f]) for f in FRONTES if f in sheets}

st.sidebar.markdown('### Filtros')
front_filter = st.sidebar.multiselect('Frente', FRONTES, default=FRONTES)
macro_all = sorted({str(x) for f,df in fronts.items() if f in front_filter and 'Macroetapa' in df for x in df['Macroetapa'].dropna().unique()})
macro_filter = st.sidebar.multiselect('Macroetapa', macro_all, default=macro_all)
status_all = sorted({str(x) for f,df in fronts.items() if f in front_filter and 'Status' in df for x in df['Status'].dropna().unique()})
status_filter = st.sidebar.multiselect('Status', status_all, default=status_all)
st.sidebar.caption(f'Base: {source_name}')

frames=[]
for f, df in fronts.items():
    if f not in front_filter: continue
    d=df.copy(); d['Frente']=f
    if 'Macroetapa' in d: d=d[d['Macroetapa'].astype(str).isin(macro_filter)]
    if 'Status' in d: d=d[d['Status'].astype(str).isin(status_filter)]
    frames.append(d)
base=pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

st.markdown('<div class="main-title"><h1>Mobilização | Aqua Pernambuco – Enorsul</h1><p>Leitura • Cobrança • Hidrometria | Go-Live 26/10/2026</p></div>', unsafe_allow_html=True)

today=date.today(); days=max((GO_LIVE-today).days,0)
total=len(base)
concl=(base['Status'].eq('Concluído').sum() if total and 'Status' in base else 0)
em_and=(base['Status'].eq('Em andamento').sum() if total and 'Status' in base else 0)
aguarda=(base['Status'].eq('Aguardando Aqua').sum() if total and 'Status' in base else 0)
atras=(base['Alerta'].eq('ATRASADO').sum() if total and 'Alerta' in base else 0)
pct=(concl/total if total else 0)

cols=st.columns(6)
for c,label,val in zip(cols,['Dias p/ Go-Live','Mobilização','Concluídos','Em andamento','Aguardando Aqua','Atrasados'],[days,f'{pct:.1%}',concl,em_and,aguarda,atras]):
    c.metric(label,val)

st.markdown('### Visão por frente')
summary=[]
for f,df in fronts.items():
    n=len(df); cc=df['Status'].eq('Concluído').sum() if 'Status' in df else 0
    summary.append({'Frente':f,'Total':n,'Concluídos':cc,'% Conclusão':cc/n if n else 0,
                    'Em andamento':df['Status'].eq('Em andamento').sum() if 'Status' in df else 0,
                    'Aguardando Aqua':df['Status'].eq('Aguardando Aqua').sum() if 'Status' in df else 0,
                    'Atrasados':df['Alerta'].eq('ATRASADO').sum() if 'Alerta' in df else 0})
sumdf=pd.DataFrame(summary)
c1,c2=st.columns([1.1,1.9])
with c1:
    show=sumdf.copy(); show['% Conclusão']=show['% Conclusão'].map(lambda x:f'{x:.1%}')
    st.dataframe(show, hide_index=True, use_container_width=True)
with c2:
    fig=px.bar(sumdf, x='Frente', y='% Conclusão', text=sumdf['% Conclusão'].map(lambda x:f'{x:.0%}'), range_y=[0,1])
    fig.update_layout(height=320, margin=dict(l=10,r=10,t=10,b=10), yaxis_tickformat='.0%', xaxis_title=None)
    st.plotly_chart(fig, use_container_width=True)

st.markdown('### Status da mobilização')
c1,c2=st.columns(2)
with c1:
    if not base.empty:
        s=base.groupby(['Frente','Status']).size().reset_index(name='Itens')
        fig=px.bar(s,x='Frente',y='Itens',color='Status',barmode='stack',category_orders={'Status':STATUS_ORDER})
        fig.update_layout(height=350, margin=dict(l=10,r=10,t=10,b=10), xaxis_title=None)
        st.plotly_chart(fig,use_container_width=True)
with c2:
    if not base.empty and 'Macroetapa' in base:
        m=base.assign(Concluido=base['Status'].eq('Concluído').astype(int)).groupby('Macroetapa').agg(Itens=('Status','size'),Concluidos=('Concluido','sum')).reset_index()
        m['%']=m['Concluidos']/m['Itens']
        fig=px.bar(m.sort_values('%'),x='%',y='Macroetapa',orientation='h',text=m.sort_values('%')['%'].map(lambda x:f'{x:.0%}'))
        fig.update_layout(height=350, margin=dict(l=10,r=10,t=10,b=10), xaxis_tickformat='.0%', xaxis_title=None, yaxis_title=None)
        st.plotly_chart(fig,use_container_width=True)

st.markdown('### 🚨 Pontos de atenção')
if not base.empty:
    crit=base[(base.get('Status','')!='Concluído') & ((base.get('Alerta','')=='ATRASADO') | (base.get('Status','')=='Aguardando Aqua') | (base.get('Prioridade','')=='Crítica'))].copy()
    cols_keep=[c for c in ['Frente','Macroetapa','Item / Atividade','Status','Pendência / Ação','Data Prevista','Alerta'] if c in crit.columns]
    if len(crit):
        st.dataframe(crit[cols_keep], hide_index=True, use_container_width=True, height=330)
    else: st.success('Nenhum ponto crítico nos filtros selecionados.')

st.markdown('### Pessoas & Bases')
c1,c2=st.columns(2)
with c1:
    p=sheets.get('Aprovação Funcionários')
    if p is not None:
        p=p.dropna(how='all')
        st.metric('Colaboradores cadastrados', max(len(p)-0,0))
        st.dataframe(p.head(20), hide_index=True, use_container_width=True, height=260)
with c2:
    b=sheets.get('Escritórios e Bases')
    if b is not None:
        b=b.dropna(how='all')
        st.metric('Bases cadastradas', max(len(b)-0,0))
        st.dataframe(b, hide_index=True, use_container_width=True, height=260)

st.markdown('### 📋 Atualização / consulta da base')
selected=st.selectbox('Frente para consultar', FRONTES)
df=fronts[selected].copy()
view_cols=[c for c in ['ID','Macroetapa','Item / Atividade','Responsável','Prioridade','Status','Data Prevista','% Conclusão','Pendência / Ação','Observação','Alerta'] if c in df.columns]
st.data_editor(df[view_cols], hide_index=True, use_container_width=True, height=500, disabled=False, key=f'editor_{selected}')
st.caption('Nesta primeira versão, o editor serve para revisão em tela. A gravação permanente no arquivo será habilitada na próxima etapa para evitar sobrescrever a base sem controle de versão.')
