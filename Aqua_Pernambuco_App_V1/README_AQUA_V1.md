# Aqua Pernambuco — Mobilização Operacional V1

Aplicação reconstruída do zero a partir da planilha `Base_Aqua_Mobilizacao_FINAL_Validada.xlsx` e da referência visual aprovada.

## Regra central

**ID Único Equipe / Agente = efetivo real.** O mesmo ID pode aparecer em várias linhas para preservar a cobertura territorial. Os KPIs contam IDs distintos; o detalhamento preserva todos os vínculos Polo → Microrrota → Município.

## Rodar localmente / Codespaces

1. Coloque estes arquivos na mesma pasta:
   - `app_aqua_v1.py`
   - `Base_Aqua_Mobilizacao_FINAL_Validada.xlsx`
   - `requirements_aqua_v1.txt`
2. Instale dependências: `pip install -r requirements_aqua_v1.txt`
3. Rode: `streamlit run app_aqua_v1.py`

## O que já funciona

- Filtros por Frente, Região, Polo, Microrrota e Status.
- KPIs deduplicados por ID único.
- Veículos disponíveis sem qualquer lógica de motocicleta.
- Distribuição por frente e status.
- Mobilização por polo.
- Planejado × mobilizado usando a aba Rampagem.
- Microrrotas por polo.
- Detalhamento/auditoria mantendo todos os vínculos territoriais.
- Validação de conflitos quando o mesmo ID aparece com dados principais divergentes.
- Alerta para registros marcados como fictícios/teste.
- Upload de nova planilha na área administrativa para teste da atualização.
- Mapa central de Pernambuco sem inventar coordenadas; marcadores só aparecem quando Latitude/Longitude oficiais existirem.

## Deliberadamente fora desta V1

- Cloudflare Worker e D1: entram depois da aprovação visual/funcional do front-end.
- Persistência do upload: nesta V1 o arquivo carregado vale apenas para a sessão Streamlit.
- Coordenadas aproximadas: não são usadas.
- Evolução histórica temporal: a planilha atual não possui histórico mensal validado suficiente para fabricar uma série.

## Próxima etapa após aprovação

Conectar o mesmo modelo lógico a uma API nova e a um D1 novo, preservando a separação entre `equipes` e `equipe_cobertura`.
