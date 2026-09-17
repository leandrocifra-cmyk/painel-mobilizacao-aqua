import json
from datetime import date, datetime
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
try:
    from supabase import create_client
except ImportError:
    create_client = None

st.set_page_config(page_title='Mobilização Aqua | Enorsul', page_icon='📊', layout='wide')
GO_LIVE=date(2026,10,26); FRONTES=['Leitura','Cobrança','Hidrometria']; STATUS=['Não iniciado','Em andamento','Aguardando Aqua','Concluído','Cancelado']
PRIO={'Crítica':0,'Alta':1,'Média':2,'Baixa':3}
st.markdown('''<style>.block-container{padding-top:.8rem}.hero{background:#0b3b78;color:white;padding:18px 22px;border-radius:10px}.hero h1{margin:0;font-size:28px}.hero p{margin:4px 0 0}.card{border:1px solid #dfe6ee;border-left:5px solid #0b3b78;border-radius:8px;padding:10px 13px;margin:7px 0;background:white}.muted{color:#64748b;font-size:.86rem}[data-testid="stMetric"]{background:#f7f9fc;border:1px solid #e2e8f0;padding:12px;border-radius:10px}</style>''',unsafe_allow_html=True)

def seed(name): return json.loads(Path(__file__).with_name(name).read_text(encoding='utf-8'))
@st.cache_resource
def db(): return create_client(st.secrets['SUPABASE_URL'],st.secrets['SUPABASE_KEY'])
def connected(): return create_client is not None and 'SUPABASE_URL' in st.secrets and 'SUPABASE_KEY' in st.secrets

def seed_table(table,file):
    cli=db(); r=cli.table(table).select('id',count='exact').limit(1).execute()
    if (r.count or 0)==0:
        rows=seed(file)
        for i in range(0,len(rows),40): cli.table(table).insert(rows[i:i+40]).execute()

def load_all():
    if not connected(): return pd.DataFrame(seed('seed_mobilizacao.json')),pd.DataFrame(seed('seed_pessoas.json')),pd.DataFrame(seed('seed_rampagem.json')),False
    for t,f in [('mobilizacao','seed_mobilizacao.json'),('pessoas_resumo','seed_pessoas.json'),('rampagem','seed_rampagem.json')]: seed_table(t,f)
    cli=db(); m=pd.DataFrame(cli.table('mobilizacao').select('*').order('frente').order('item_id').execute().data); p=pd.DataFrame(cli.table('pessoas_resumo').select('*').order('frente').execute().data); r=pd.DataFrame(cli.table('rampagem').select('*').order('frente').order('ordem').execute().data)
    return m,p,r,True

def dt(v):
    try:
        if v in [None,''] or pd.isna(v): return None
        return pd.to_datetime(v).date()
    except:return None

def next_step(row,fd):
    manual=str(row.get('proximo_passo_manual') or '').strip(); pend=str(row.get('pendencia') or '').strip(); s=row.get('status')
    if manual:return manual
    if s=='Concluído':return 'Etapa concluída.'
    if s=='Cancelado':return 'Validar impacto do cancelamento nas atividades dependentes.'
    if s=='Aguardando Aqua':return pend or 'Cobrar retorno/validação da Aqua.'
    if s=='Em andamento':return pend or 'Concluir atividade e registrar evidência.'
    prev=fd[(fd.macroetapa==row.get('macroetapa'))&(fd.item_id<row.get('item_id',0))&(~fd.status.isin(['Concluído','Cancelado']))]
    if len(prev): return f"Avançar após tratar: {prev.sort_values('item_id').iloc[-1].atividade}."
    return pend or 'Iniciar atividade e registrar responsável, prazo e evidência.'

def score(r):
    if r.status in ['Concluído','Cancelado']:return (9,9,date.max)
    p=dt(r.get('data_prevista')); overdue=p and p<date.today(); due7=p and 0<=(p-date.today()).days<=7
    return (0 if overdue else 1 if r.status=='Aguardando Aqua' else 2 if due7 else 3,PRIO.get(r.get('prioridade'),4),p or date.max)

def next_df(df):
    out=[]
    for _,r in df.iterrows():
        if r.status in ['Concluído','Cancelado']:continue
        out.append({'Frente':r.frente,'Atividade':r.atividade,'Status':r.status,'Prioridade':r.get('prioridade',''),'Data Prevista':r.get('data_prevista'),'Próximo Passo':next_step(r,df[df.frente==r.frente]),'_s':score(r)})
    return pd.DataFrame(sorted(out,key=lambda x:x['_s'])) if out else pd.DataFrame()

def auth(pin): return (not persistent) or pin==st.secrets.get('APP_PIN','')
def update(table,row_id,vals): vals['atualizado_em']=datetime.now().isoformat(); db().table(table).update(vals).eq('id',int(row_id)).execute()

try:m,pessoas,ramp,persistent=load_all()
except Exception as e: st.error('A base online ainda não está configurada corretamente.');st.code(str(e));st.stop()

st.markdown('<div class="hero"><h1>Mobilização | Aqua Pernambuco – Enorsul</h1><p>Central de gestão • Leitura • Cobrança • Hidrometria | Go-Live 26/10/2026</p></div>',unsafe_allow_html=True)
if not persistent:st.info('Modo de teste no Codespaces: dados iniciais carregados. A conexão online fica opcional para a etapa de publicação.')
ativos=m[m.status!='Cancelado']; dias=max((GO_LIVE-date.today()).days,0); total=len(ativos); concl=int((ativos.status=='Concluído').sum()); pct=concl/total if total else 0
cols=st.columns(6)
vals=[dias,f'{pct:.1%}',concl,int((ativos.status=='Em andamento').sum()),int((ativos.status=='Aguardando Aqua').sum()),int((ativos.status=='Não iniciado').sum())]
for c,l,v in zip(cols,['Dias p/ Go-Live','Mobilização','Concluídos','Em andamento','Aguardando Aqua','Não iniciados'],vals):c.metric(l,v)

pages=['Visão Geral','Leitura','Cobrança','Hidrometria','Pessoas & Estrutura','Cronograma & Rampagem','Modo Reunião']
page=st.radio('Navegação',pages,horizontal=True,label_visibility='collapsed')

def resumo_frentes():
    a=[]
    for f in FRONTES:
        x=m[(m.frente==f)&(m.status!='Cancelado')]; n=len(x); c=int((x.status=='Concluído').sum())
        a.append({'Frente':f,'Itens':n,'Concluídos':c,'% Conclusão':c/n if n else 0,'Em andamento':int((x.status=='Em andamento').sum()),'Aguardando Aqua':int((x.status=='Aguardando Aqua').sum())})
    return pd.DataFrame(a)

if page=='Visão Geral':
    rd=resumo_frentes(); a,b=st.columns([1,1.5]);
    with a:
        sh=rd.copy();sh['% Conclusão']=sh['% Conclusão'].map(lambda x:f'{x:.1%}');st.dataframe(sh,hide_index=True,use_container_width=True)
    with b:
        fig=px.bar(rd,x='Frente',y='% Conclusão',text=rd['% Conclusão'].map(lambda x:f'{x:.0%}'),range_y=[0,1]);fig.update_layout(height=300,margin=dict(l=10,r=10,t=10,b=10),yaxis_tickformat='.0%',xaxis_title=None);st.plotly_chart(fig,use_container_width=True)
    st.markdown('### Próximos Passos Prioritários'); nt=next_df(m)
    for _,r in nt.head(10).iterrows():st.markdown(f"<div class='card'><b>{r['Frente']} | {r['Atividade']}</b><br><span class='muted'>{r['Status']} • {r['Prioridade']} • Previsto: {r['Data Prevista'] or '-'}</span><br>{r['Próximo Passo']}</div>",unsafe_allow_html=True)
    st.markdown('### Rampagem executiva'); rr=ramp[ramp.frente.isin(['Cobrança','Hidrometria'])].copy(); fig=px.line(rr,x='mes',y='equipes_planejadas',color='frente',markers=True,text='equipes_planejadas');fig.update_layout(height=330,xaxis_title=None,yaxis_title='Equipes planejadas');st.plotly_chart(fig,use_container_width=True)

elif page in FRONTES:
    f=page; fd=m[m.frente==f].sort_values('item_id'); x=fd[fd.status!='Cancelado']; st.markdown(f'## Implantação – {f}')
    cs=st.columns(5); vv=[len(x),int((x.status=='Concluído').sum()),int((x.status=='Em andamento').sum()),int((x.status=='Aguardando Aqua').sum()),int((x.status=='Não iniciado').sum())]
    for c,l,v in zip(cs,['Itens','Concluídos','Em andamento','Aguardando Aqua','Não iniciados'],vv):c.metric(l,v)
    nt=next_df(fd); st.markdown('### Próximos passos');
    if len(nt):st.dataframe(nt.drop(columns='_s').head(8),hide_index=True,use_container_width=True)
    st.markdown('### Atualizar implantação'); choices={f"{int(r.item_id):02d} — {r.atividade}":i for i,r in fd.iterrows()}; key=st.selectbox('Item / atividade',list(choices)); r=fd.loc[choices[key]]
    with st.form('atividade'):
        c1,c2,c3=st.columns(3); status=c1.selectbox('Status',STATUS,index=STATUS.index(r.status) if r.status in STATUS else 0); perc=c2.number_input('% de avanço',0,100,int(r.get('percentual') or 0),5); prev=c3.date_input('Data prevista',dt(r.get('data_prevista')) or date.today()); pend=st.text_area('Pendência / Ação',str(r.get('pendencia') or '')); prox=st.text_area('Próximo passo manual (opcional)',str(r.get('proximo_passo_manual') or '')); obs=st.text_area('Observação',str(r.get('observacao') or '')); evid=st.text_input('Evidência / referência',str(r.get('evidencia') or '')); nome=st.text_input('Atualizado por'); pin=st.text_input('Senha de atualização',type='password') if persistent else ''; save=st.form_submit_button('Salvar atualização',type='primary',use_container_width=True)
    if save:
        if not persistent:st.error('Configure a base online antes de salvar.')
        elif not auth(pin):st.error('Senha incorreta.')
        else:
            update('mobilizacao',r.id,{'status':status,'percentual':100 if status=='Concluído' else perc,'data_prevista':prev.isoformat(),'data_conclusao':date.today().isoformat() if status=='Concluído' else None,'pendencia':pend or None,'proximo_passo_manual':prox or None,'observacao':obs or None,'evidencia':evid or None,'atualizado_por':nome or 'Não informado'});st.success('Atualização salva.');st.rerun()
    sh=fd[['item_id','macroetapa','atividade','prioridade','status','percentual','data_prevista','pendencia']].copy();sh.columns=['ID','Macroetapa','Atividade','Prioridade','Status','%','Data Prevista','Pendência / Ação'];st.dataframe(sh,hide_index=True,use_container_width=True,height=440)

elif page=='Pessoas & Estrutura':
    st.markdown('## Pessoas & Estrutura'); st.caption('Acompanhamento consolidado por frente/grupo. Evita expor dados pessoais na visão executiva.')
    if len(pessoas):
        totals=pessoas[['planejado','disponivel','documentacao_enviada','aprovado_aqua','integrado','liberado_campo']].sum(); cs=st.columns(6)
        for c,l,k in zip(cs,['Planejado','Disponível','Docs enviados','Aprovado Aqua','Integrado','Liberado campo'],totals.index):c.metric(l,int(totals[k]))
        st.dataframe(pessoas[['frente','grupo','planejado','disponivel','documentacao_enviada','aprovado_aqua','integrado','liberado_campo','observacao']],hide_index=True,use_container_width=True)
        if persistent:
            opts={f"{r.frente} — {r.grupo}":i for i,r in pessoas.iterrows()}; sel=st.selectbox('Atualizar grupo',list(opts)); r=pessoas.loc[opts[sel]]
            with st.form('pessoas'):
                cs=st.columns(6); nums=[]
                for c,l,k in zip(cs,['Planejado','Disponível','Docs enviados','Aprovado Aqua','Integrado','Liberado campo'],['planejado','disponivel','documentacao_enviada','aprovado_aqua','integrado','liberado_campo']): nums.append(c.number_input(l,0,5000,int(r.get(k) or 0)))
                obs=st.text_area('Observação',str(r.get('observacao') or ''));nome=st.text_input('Atualizado por');pin=st.text_input('Senha',type='password');sv=st.form_submit_button('Salvar pessoas',type='primary')
            if sv:
                if not auth(pin):st.error('Senha incorreta.')
                else:
                    vals=dict(zip(['planejado','disponivel','documentacao_enviada','aprovado_aqua','integrado','liberado_campo'],nums));vals.update({'observacao':obs,'atualizado_por':nome or 'Não informado'});update('pessoas_resumo',r.id,vals);st.rerun()

elif page=='Cronograma & Rampagem':
    st.markdown('## Cronograma & Rampagem'); front=st.selectbox('Frente',FRONTES)
    rr=ramp[ramp.frente==front].sort_values('ordem'); st.markdown('### Rampagem / estrutura planejada')
    st.dataframe(rr[['mes','equipes_planejadas','equipes_mobilizadas','veiculos_planejados','veiculos_mobilizados','observacao']],hide_index=True,use_container_width=True)
    if front in ['Cobrança','Hidrometria']:
        long=rr.melt(id_vars=['mes'],value_vars=['equipes_planejadas','equipes_mobilizadas'],var_name='Série',value_name='Equipes');fig=px.bar(long,x='mes',y='Equipes',color='Série',barmode='group');st.plotly_chart(fig,use_container_width=True)
    if persistent and len(rr):
        opts={str(r.mes):i for i,r in rr.iterrows()};sel=st.selectbox('Atualizar período/região',list(opts));r=rr.loc[opts[sel]]
        with st.form('ramp'):
            c1,c2=st.columns(2); em=c1.number_input('Equipes mobilizadas',0,500,int(r.equipes_mobilizadas or 0));vm=c2.number_input('Veículos mobilizados',0,500,int(r.veiculos_mobilizados or 0));obs=st.text_area('Observação',str(r.observacao or ''));nome=st.text_input('Atualizado por');pin=st.text_input('Senha',type='password');sv=st.form_submit_button('Salvar rampagem',type='primary')
        if sv:
            if not auth(pin):st.error('Senha incorreta.')
            else:update('rampagem',r.id,{'equipes_mobilizadas':em,'veiculos_mobilizados':vm,'observacao':obs,'atualizado_por':nome or 'Não informado'});st.rerun()
    st.markdown('### Cronograma de implantação'); cr=m[(m.frente==front)&m.data_prevista.notna()].copy(); cr['Fim']=pd.to_datetime(cr.data_prevista); cr['Início']=cr['Fim']-pd.to_timedelta(3,unit='D'); fig=px.timeline(cr,x_start='Início',x_end='Fim',y='atividade',color='status',hover_data=['macroetapa','prioridade']);fig.update_yaxes(autorange='reversed');fig.update_layout(height=max(420,len(cr)*25),xaxis_title=None,yaxis_title=None);st.plotly_chart(fig,use_container_width=True)

else:
    st.markdown('## Modo Reunião');st.caption('Visão limpa para acompanhamento com a Aqua.')
    rd=resumo_frentes(); cs=st.columns(3)
    for c,(_,r) in zip(cs,rd.iterrows()):c.metric(r.Frente,f"{r['% Conclusão']:.1%}",f"{r['Concluídos']}/{r['Itens']} concluídos")
    st.markdown('### Pontos que exigem ação');nt=next_df(m)
    if len(nt):st.dataframe(nt.drop(columns='_s').head(10),hide_index=True,use_container_width=True)
    st.markdown('### Rampagem');rr=ramp[ramp.frente.isin(['Cobrança','Hidrometria'])];fig=px.line(rr,x='mes',y='equipes_planejadas',color='frente',markers=True,text='equipes_planejadas');st.plotly_chart(fig,use_container_width=True)
    st.markdown('### Situação de pessoas');
    if len(pessoas):st.dataframe(pessoas.groupby('frente')[['planejado','disponivel','documentacao_enviada','aprovado_aqua','integrado','liberado_campo']].sum(),use_container_width=True)
