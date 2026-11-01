# Research: Portal de Relatórios de Tráfego Pago

**Date**: 2026-10-31

## R1: Metabase Guest Embed vs. Signed Embed

**Decision**: Usar Metabase signed embedding (JWT) via METABASE_SECRET_KEY.

**Rationale**: O guest embed (public) não permite travar filtros por usuário. O signed embed gera um JWT no Flask com o filtro `empresa_id` locked, impedindo que o cliente manipule o filtro no front-end. Isso garante isolamento multi-tenant no nível do dashboard.

**Alternatives considered**:
- Guest embed (público): descartado por não suportar filtros travados.
- Metabase API + gráficos customizados (Recharts/Chart.js): mais controle visual, mas complexidade muito maior para o MVP. Pode ser considerado na Fase 2.
- iframe com token temporário: essencialmente o que o signed embed faz nativamente.

## R2: facebook-business SDK — campos e rate limits

**Decision**: Usar o SDK `facebook-business` (Python) com endpoints Campaign, AdSet, Ad e AdCreative. Campos: impressions, clicks, spend, actions (leads), cost_per_action_type. Criativos via Ad → AdCreative (thumbnail_url, title, body).

**Rationale**: O SDK oficial abstrai paginação e rate limits. O Marketing API permite buscar Insights por account com breakdowns por campanha/adset/ad. Rate limit: 200 chamadas por hora por app em produção (System User token). Com batch requests, 50 clientes cabem confortavelmente em um ciclo horário.

**Alternatives considered**:
- Requests diretas à Graph API: mais controle, mas reimplementa paginação e retry.
- Airbyte/Fivetran open source: overhead de infra desnecessário para MVP.

## R3: Sincronização — RQ + Redis vs. Cron puro

**Decision**: RQ (Redis Queue) com worker dedicado. Job agendado via `rq-scheduler` ou cron do Railway (Schedule section no railway.toml).

**Rationale**: RQ permite retry automático, job isolation (um erro não bloqueia os demais), e filas nomeadas. Redis já é necessário para o Metabase (cache interno). O cron do Railway dispara o enqueue; o worker processa. Cada cliente vira um job independente na fila.

**Alternatives considered**:
- Celery: mais features mas overhead desnecessário para MVP com poucos jobs.
- APScheduler in-process: risco de memory leaks e não sobrevive a restart.
- Cron puro (subprocess): sem retry, sem isolamento de falhas entre clientes.

## R4: Criptografia de tokens — Fernet (cryptography)

**Decision**: `cryptography.fernet.Fernet` com chave derivada de variável de ambiente `FERNET_KEY`.

**Rationale**: Fernet é symmetric authenticated encryption (AES-128-CBC + HMAC-SHA256). A chave fica em variável de ambiente do Railway (nunca no repo). Encrypt no momento de salvar o OAuth token; decrypt no momento de usar no SDK do Meta. Token descriptografado nunca persiste em disco ou log.

**Alternatives considered**:
- PGP/GPG: assimétrico, desnecessário para este caso.
- Vault/SOPS: overhead de infra para MVP.
- Column-level encryption do PostgreSQL (pgcrypto): viable mas acopla ao banco; Fernet no app dá mais portabilidade.

## R5: PDF Export — WeasyPrint vs. alternativas

**Decision**: WeasyPrint para renderizar HTML → PDF no servidor.

**Rationale**: O painel já é HTML/CSS (Tailwind). WeasyPrint renderiza templates Jinja2 com dados pré-carregados direto em PDF. Funciona headless em Docker (precisa de dependências Cairo/Pango no Dockerfile). Para os dashboards do Metabase, capturar screenshots seria complexo; a alternativa é gerar um template PDF-specific com os mesmos dados (queries diretas ao banco, não via Metabase).

**Alternatives considered**:
- Puppeteer/Playwright (screenshot do Metabase): complexo, precisa de browser headless no container.
- ReportLab: mais baixo nível, sem reuso dos templates HTML.
- wkhtmltopdf: deprecated, problemas com Tailwind CSS moderno.

## R6: Metabase — configuração e dashboards

**Decision**: Metabase OSS em container Docker dedicado no Railway. Dashboards pré-configurados manualmente na UI do Metabase; embed via signed JWT.

**Rationale**: Metabase conecta direto ao mesmo PostgreSQL do portal. Os 6 widgets do painel são questions/cards no Metabase agrupados em um dashboard. O filtro `empresa_id` é um filter widget locked via JWT. Configuração inicial manual (one-time setup); depois, cada novo cliente funciona automaticamente pelo filtro.

**Alternatives considered**:
- Configuração via API do Metabase (automação): possível para Fase 2.
- Apache Superset: mais complexo de operar e sem embed tão simples.
- Grafana: melhor para métricas de infra, não para dashboards de negócio.

## R7: Camada de serviço para IA (Fase 2)

**Decision**: Criar `app/services/` como camada de serviço separada dos blueprints. Cada serviço é uma classe ou módulo com interface clara (input → output). Na Fase 2, um serviço `ai_insights.py` pode consumir dados dos outros serviços.

**Rationale**: Separar regras de negócio (services/) dos handlers HTTP (blueprints/routes.py) permite que a Fase 2 plugue IA sem refatorar rotas. O serviço de IA chamaria `meta_ads.get_metricas()` e `leads.get_funil()` para montar contexto para a OpenAI API.

**Alternatives considered**:
- Tudo em routes.py: funciona para MVP mas dificulta a extensão.
- Microserviço separado para IA: overhead de infra desnecessário; um módulo no mesmo app é suficiente para Fase 2.
