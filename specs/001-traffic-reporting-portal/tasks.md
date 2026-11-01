# Tasks: Portal de Relatórios de Tráfego Pago

**Input**: Design documents from `/specs/001-traffic-reporting-portal/`

**Prerequisites**: plan.md, spec.md, data-model.md, contracts/routes.md, research.md, quickstart.md

**Tests**: Incluídos para regras de permissão e verba (obrigatório pela constituição, Princípio VI).

**Organization**: Tasks agrupadas por user story para implementação e teste independentes.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Inicialização do projeto, Docker, dependências e estrutura base

- [ ] T001 Create project root structure: `app/`, `app/models/`, `app/blueprints/`, `app/services/`, `app/templates/`, `app/static/css/`, `tests/`
- [ ] T002 Create `requirements.txt` with pinned dependencies: Flask>=3.0, Flask-Login>=0.6, SQLAlchemy>=2.0, alembic, psycopg2-binary, redis, rq, facebook-business, cryptography, PyJWT, WeasyPrint, python-dotenv, ruff, pytest
- [ ] T003 [P] Create `Dockerfile` for portal service: Python 3.11-slim base, install WeasyPrint system deps (libcairo2, libpango), pip install requirements, EXPOSE 5000, gunicorn entrypoint
- [ ] T004 [P] Create `docker-compose.yml` with 4 services: portal (build .), postgres (image postgres:16, volume pgdata, POSTGRES_DB=getraf), redis (image redis:7-alpine), metabase (image metabase/metabase:latest, MB_DB_TYPE=postgres, depends_on postgres)
- [ ] T005 [P] Create `.env.example` with all required env vars: SECRET_KEY, DATABASE_URL (postgresql://getraf:getraf@postgres:5432/getraf), REDIS_URL (redis://redis:6379/0), FERNET_KEY, META_APP_ID, META_APP_SECRET, META_REDIRECT_URI, METABASE_SECRET_KEY, METABASE_SITE_URL
- [ ] T006 [P] Create `.gitignore` with Python defaults, .env, __pycache__, *.pyc, .pytest_cache, instance/
- [ ] T007 Create `app/config.py` with Config classes: Config (base, reads from env), DevelopmentConfig (DEBUG=True), TestingConfig (TESTING=True, SQLALCHEMY_DATABASE_URI=sqlite:///:memory:), ProductionConfig

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: App factory, DB, modelos base, autenticação, decorators, serviço de crypto. DEVE completar antes de qualquer user story.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T008 Create `app/extensions.py`: initialize SQLAlchemy (db), Migrate (migrate), LoginManager (login_manager), Fernet instance (loaded from FERNET_KEY env var)
- [ ] T009 Create `app/__init__.py` with `create_app(config_name)` factory: load config, init extensions (db, migrate, login_manager), register blueprints (auth, gestor, cliente, leads), configure login_manager.login_view='auth.login', login_manager.login_message in pt-BR
- [ ] T010 Create `app/models/__init__.py` importing all models for Alembic discovery
- [ ] T011 Create `app/models/usuario.py`: Usuario model with fields — id (UUID, PK, default uuid4), email (String(255), UNIQUE, NOT NULL), senha_hash (String(255), NOT NULL), nome (String(150), NOT NULL), perfil (Enum: 'gestor_dono','gestor','cliente', NOT NULL), status (Enum: 'pendente','ativo','inativo', NOT NULL, default 'pendente'), empresa_id (UUID, FK Empresa.id, NULLABLE), criado_em (DateTime, NOT NULL, default utcnow), atualizado_em (DateTime, NOT NULL, onupdate utcnow). Implement UserMixin for Flask-Login. Method `set_senha(plain)` hashes with bcrypt; `check_senha(plain)` verifies. user_loader callback on login_manager.
- [ ] T012 [P] Create `app/models/empresa.py`: Empresa model with fields — id (UUID, PK), nome (String(200), NOT NULL), segmento (String(100), NULLABLE), teto_verba_mensal (Numeric(12,2), NULLABLE, CHECK > 0 when not null), gestor_id (UUID, FK Usuario.id, NOT NULL), status_conexao (Enum: 'aguardando','conectado','reconexao_necessaria', NOT NULL, default 'aguardando'), criado_em (DateTime, NOT NULL), atualizado_em (DateTime, NOT NULL). Relationship: gestor = relationship('Usuario'), contas = relationship('ContaAnuncio'), leads = relationship('Lead')
- [ ] T013 [P] Create `app/models/log_auditoria.py`: LogAuditoria model with fields — id (UUID, PK), empresa_id (UUID, FK Empresa.id, NOT NULL), usuario_id (UUID, FK Usuario.id, NOT NULL), acao (String(100), NOT NULL), entidade_tipo (String(50), NOT NULL), entidade_id (UUID, NOT NULL), dados_anteriores (JSON, NULLABLE), dados_novos (JSON, NULLABLE), criado_em (DateTime, NOT NULL, default utcnow). Table is APPEND-ONLY: no update/delete methods exposed.
- [ ] T014 Create `app/services/crypto.py`: encrypt_token(plain_text) → bytes (Fernet encrypt), decrypt_token(cipher_bytes) → str (Fernet decrypt). Uses Fernet instance from extensions. NEVER log plain text tokens.
- [ ] T015 Create `app/services/auditoria.py`: registrar_acao(empresa_id, usuario_id, acao, entidade_tipo, entidade_id, dados_anteriores=None, dados_novos=None) → creates LogAuditoria record and commits. No update or delete functions.
- [ ] T016 Create `app/decorators.py`: `role_required(*perfis)` decorator — checks current_user.perfil in allowed perfis, returns 403 if not. `empresa_required` decorator — validates current_user has access to the empresa_id in the route (cliente sees only own empresa, gestor sees only assigned empresas, gestor_dono sees all).
- [ ] T017 Initialize Alembic: `flask db init`, create initial migration with Usuario, Empresa, LogAuditoria tables, run `flask db upgrade`
- [ ] T018 Create `app/blueprints/auth/__init__.py` and `app/blueprints/auth/forms.py`: LoginForm (email, senha), RegistroForm (nome, email, senha, confirmar_senha with EqualTo validator)
- [ ] T019 Create `app/blueprints/auth/routes.py`: GET/POST /login (authenticate, login_user, redirect by perfil), GET /logout (logout_user), GET/POST /registro (create Usuario with perfil='gestor', status='pendente')
- [ ] T020 [P] Create `app/templates/base.html`: HTML5 base layout with Tailwind CSS CDN, nav bar (shows user name, logout link), flash messages area, block content. All text in pt-BR.
- [ ] T021 [P] Create `app/templates/auth/login.html` and `app/templates/auth/registro.html`: extends base.html, forms in pt-BR, error display
- [ ] T022 Create `tests/conftest.py`: pytest fixtures — app (create_app('testing')), db (create_all/drop_all), client (app.test_client), usuario_gestor_dono (perfil='gestor_dono', status='ativo'), usuario_gestor (perfil='gestor', status='ativo'), usuario_cliente (perfil='cliente', status='ativo', empresa_id set), empresa fixture with gestor_id
- [ ] T023 Create `tests/test_auth.py`: test login success, login wrong password, logout redirect, registro creates user with status pendente, registro duplicate email fails
- [ ] T024 Create `tests/test_permissoes.py`: test gestor_dono can access /gestor/gestores, gestor cannot access /gestor/gestores (403), cliente cannot access /gestor/clientes (403), cliente accessing another empresa's leads returns 403, gestor accessing another gestor's empresa returns 403, unauthenticated user redirected to login. Constitution Principle II: cross-tenant isolation tests.
- [ ] T025 Create `tests/test_crypto.py`: test encrypt_token returns bytes, decrypt_token recovers original, encrypted token is not equal to plaintext, decrypt with wrong key raises error
- [ ] T026 Create CLI command `flask create-owner` in `app/__init__.py`: creates gestor_dono user with email/nome/senha args, status='ativo'. Used for initial setup.

**Checkpoint**: Foundation ready — auth works, models created, decorators enforce access control, crypto service functional. User story implementation can begin.

---

## Phase 3: User Story 1 — Gestor cadastra cliente e conecta Meta (Priority: P1) 🎯 MVP

**Goal**: Gestor faz login, cadastra uma empresa (cliente) com nome/segmento/teto, e conecta a conta de anúncios do Meta via OAuth. Token armazenado criptografado.

**Independent Test**: Criar cliente, conectar conta Meta de teste, verificar que token está criptografado no banco e empresa está com status "conectado".

### Implementation for User Story 1

- [ ] T027 [P] [US1] Create `app/models/conta_anuncio.py`: ContaAnuncio model with fields — id (UUID, PK), empresa_id (UUID, FK Empresa.id, NOT NULL), plataforma (Enum: 'meta','google', NOT NULL), conta_id_externo (String(100), NOT NULL), token_criptografado (LargeBinary, NOT NULL), token_expira_em (DateTime, NULLABLE), status (Enum: 'ativo','expirado','revogado', NOT NULL, default 'ativo'), criado_em, atualizado_em. UNIQUE constraint on (empresa_id, plataforma). Token field MUST NOT be included in any __repr__ or serialization.
- [ ] T028 [US1] Create Alembic migration for ContaAnuncio table, run `flask db upgrade`
- [ ] T029 [US1] Create `app/services/meta_ads.py`: get_oauth_url(redirect_uri, state) → Facebook OAuth URL with scopes ads_read. exchange_code_for_token(code, redirect_uri) → access_token string using facebook-business SDK. get_ad_accounts(access_token) → list of ad account IDs.
- [ ] T030 [US1] Create `app/blueprints/gestor/__init__.py` and `app/blueprints/gestor/forms.py`: ClienteForm (nome: StringField required max 200, segmento: StringField optional max 100, teto_verba_mensal: DecimalField optional validators=[Optional(), NumberRange(min=0.01)])
- [ ] T031 [US1] Create `app/blueprints/gestor/routes.py` — client CRUD routes: GET /gestor/clientes (list empresas where gestor_id=current_user.id; gestor_dono sees all), GET /gestor/clientes/novo (render form), POST /gestor/clientes/novo (validate form, create Empresa with gestor_id=current_user.id, status_conexao='aguardando', registrar_acao in auditoria), GET /gestor/clientes/<id> (detail page, check empresa_required)
- [ ] T032 [US1] Add Meta OAuth routes to `app/blueprints/gestor/routes.py`: GET /gestor/clientes/<id>/conectar-meta (validate empresa_required, call meta_ads.get_oauth_url, redirect), GET /gestor/clientes/<id>/meta-callback (exchange code, encrypt token with crypto.encrypt_token, save ContaAnuncio, update Empresa.status_conexao='conectado', registrar_acao)
- [ ] T033 [P] [US1] Create `app/templates/gestor/clientes.html`: table listing empresas with nome, segmento, status_conexao, link to detail. Button "Novo Cliente".
- [ ] T034 [P] [US1] Create `app/templates/gestor/cliente_form.html`: form for ClienteForm, submit button "Cadastrar"
- [ ] T035 [P] [US1] Create `app/templates/gestor/cliente_detalhe.html`: empresa details, status_conexao indicator, button "Conectar Meta" (if status aguardando/reconexao), link to leads

**Checkpoint**: Gestor pode cadastrar clientes e conectar conta Meta. Token criptografado no banco. Empresa com status "conectado".

---

## Phase 4: User Story 5 — Sincronização automática de métricas (Priority: P1)

**Goal**: Job horário busca métricas do Meta Ads para todos os clientes conectados, grava na tabela metrica_diaria. Erros isolados por cliente.

**Independent Test**: Com cliente conectado, disparar `flask sync-metricas`, verificar que métricas aparecem na tabela metrica_diaria.

### Implementation for User Story 5

- [ ] T036 [P] [US5] Create `app/models/metrica_diaria.py`: MetricaDiaria model with fields — id (UUID, PK), empresa_id (UUID, FK Empresa.id, NOT NULL), conta_anuncio_id (UUID, FK ContaAnuncio.id, NOT NULL), data (Date, NOT NULL), campanha_id (String(100), NOT NULL), campanha_nome (String(300), NOT NULL), conjunto_id (String(100), NULLABLE), conjunto_nome (String(300), NULLABLE), anuncio_id (String(100), NULLABLE), anuncio_nome (String(300), NULLABLE), impressoes (Integer, NOT NULL, default 0), cliques (Integer, NOT NULL, default 0), gasto (Numeric(12,2), NOT NULL, default 0), leads_gerados (Integer, NOT NULL, default 0), criativo_url (String(500), NULLABLE), criativo_titulo (String(300), NULLABLE), sincronizado_em (DateTime, NOT NULL). UNIQUE constraint on (empresa_id, data, anuncio_id). Index on (empresa_id, data).
- [ ] T037 [US5] Create Alembic migration for MetricaDiaria table, run `flask db upgrade`
- [ ] T038 [US5] Extend `app/services/meta_ads.py`: get_insights(access_token, account_id, date_start, date_end) → list of dicts with fields: campaign_id, campaign_name, adset_id, adset_name, ad_id, ad_name, impressions, clicks, spend, actions (leads), creative thumbnail_url, creative title. Uses facebook-business SDK AdAccount.get_insights() with breakdowns by ad.
- [ ] T039 [US5] Create `app/services/sync_metricas.py`: sync_empresa(empresa_id) — decrypt token, call get_insights for yesterday+today, upsert MetricaDiaria rows (ON CONFLICT empresa_id,data,anuncio_id DO UPDATE). On token error: update Empresa.status_conexao='reconexao_necessaria', log error but don't raise. sync_todas() — query all Empresa where status_conexao='conectado', enqueue sync_empresa for each via RQ. Each empresa is independent; one failure doesn't block others.
- [ ] T040 [US5] Create CLI command `flask sync-metricas` in `app/__init__.py`: calls sync_metricas.sync_todas() synchronously (for manual/cron trigger)
- [ ] T041 [US5] Configure RQ worker: create `worker.py` at project root that connects to Redis and listens on 'default' queue. Add worker service to `docker-compose.yml` (same image as portal, command: python worker.py)
- [ ] T042 [US5] Create `tests/test_sync.py`: test sync_empresa with mocked facebook-business SDK (mock get_insights returning sample data), verify MetricaDiaria rows created. Test sync with expired token marks empresa as reconexao_necessaria. Test upsert (running sync twice doesn't create duplicates).

**Checkpoint**: Sincronização funciona. Métricas gravadas em metrica_diaria. Erros por cliente isolados.

---

## Phase 5: User Story 2 — Cliente visualiza painel de relatórios (Priority: P1)

**Goal**: Cliente faz login e vê dashboard Metabase embeddado com 6 widgets filtrados por sua empresa. Seletor de período. Exportação PDF.

**Independent Test**: Login como cliente, painel carrega com iframe Metabase mostrando dados. Alterar período atualiza. PDF baixa com os widgets.

### Implementation for User Story 2

- [ ] T043 [US2] Create `app/services/metabase_embed.py`: generate_embed_url(dashboard_id, empresa_id, params=None) → signed URL using PyJWT. Payload: resource={"dashboard": dashboard_id}, params={"empresa_id": empresa_id} (LOCKED, cannot be changed by viewer). Signs with METABASE_SECRET_KEY. Returns full embed URL (METABASE_SITE_URL + /embed/dashboard/ + token).
- [ ] T044 [US2] Create `app/blueprints/cliente/__init__.py` and `app/blueprints/cliente/routes.py`: GET /cliente/painel (role_required('cliente'), empresa_required, generate Metabase embed URL with current_user.empresa_id locked, pass periodo_inicio/periodo_fim from query params, default last 30 days, render template)
- [ ] T045 [US2] Create `app/services/pdf_export.py`: gerar_pdf_painel(empresa_id, periodo_inicio, periodo_fim) → bytes (PDF content). Queries MetricaDiaria filtered by empresa_id and date range. Computes: investido vs contratos por semana, funil (sum impressoes, cliques, leads_gerados, count leads status orcamento, count leads status contrato), custo por lead, custo por contrato, ranking criativos by gasto, verba gasta vs teto (from Empresa.teto_verba_mensal), origem leads (group by origem_campanha). Renders `app/templates/cliente/painel_pdf.html` via WeasyPrint. All text in pt-BR.
- [ ] T046 [US2] Add PDF export route to `app/blueprints/cliente/routes.py`: GET /cliente/painel/pdf (role_required('cliente'), empresa_required, validate periodo_inicio and periodo_fim as ISO dates, call gerar_pdf_painel, return Response with content_type application/pdf and Content-Disposition attachment filename=relatorio_YYYYMMDD.pdf)
- [ ] T047 [P] [US2] Create `app/templates/cliente/painel.html`: extends base.html, date range picker (periodo_inicio, periodo_fim inputs type=date, form GET), iframe src=metabase_embed_url with style width:100% height:800px border:none, button "Exportar PDF" linking to /cliente/painel/pdf with current dates
- [ ] T048 [P] [US2] Create `app/templates/cliente/painel_pdf.html`: standalone HTML (not extends base.html) optimized for PDF rendering. Inline CSS (no Tailwind CDN). 6 sections: investido x contratos (table), funil (horizontal bar), custo por lead/contrato (table), ranking criativos (table with top 10), verba x teto (bar with highlight if exceeded), origem leads (table grouped). Header with empresa nome, período, date generated. All pt-BR.
- [ ] T049 [US2] Add route for gestor_dono to view any client's panel: GET /gestor/clientes/<id>/painel in gestor routes (role_required('gestor_dono','gestor'), empresa_required, same Metabase embed logic with empresa_id from URL param)

**Checkpoint**: Cliente vê painel completo. PDF exporta com 6 widgets. Gestor dono pode visualizar painel de qualquer cliente.

---

## Phase 6: User Story 3 — Gestão de leads (Priority: P2)

**Goal**: Lista de leads por cliente com origem, status e valor. Gestor e cliente atualizam status. Toda mudança registrada em log de auditoria.

**Independent Test**: Alterar status de lead para "contrato" com valor R$ 3.500; verificar log de auditoria e funil atualizado.

### Implementation for User Story 3

- [ ] T050 [P] [US3] Create `app/models/lead.py`: Lead model with fields — id (UUID, PK), empresa_id (UUID, FK Empresa.id, NOT NULL), nome (String(200), NULLABLE), telefone (String(50), NULLABLE), email (String(255), NULLABLE), origem_campanha (String(300), NULLABLE), origem_conjunto (String(300), NULLABLE), origem_anuncio (String(300), NULLABLE), status (Enum: 'novo','orcamento','contrato','perdido', NOT NULL, default 'novo'), valor_contrato (Numeric(12,2), NULLABLE, CHECK > 0 when not null), criado_em (DateTime, NOT NULL), atualizado_em (DateTime, NOT NULL). Index on (empresa_id, status). Index on (empresa_id, criado_em). Validation: valor_contrato MUST be set when status='contrato'. Valid transitions: novo→orcamento, novo→perdido, orcamento→contrato, orcamento→perdido, orcamento→novo.
- [ ] T051 [US3] Create Alembic migration for Lead table, run `flask db upgrade`
- [ ] T052 [US3] Create `app/blueprints/leads/__init__.py` and `app/blueprints/leads/forms.py`: LeadStatusForm (novo_status: SelectField choices=['novo','orcamento','contrato','perdido'], valor_contrato: DecimalField optional validators=[Optional(), NumberRange(min=0.01)])
- [ ] T053 [US3] Create `app/blueprints/leads/routes.py`: GET /leads/<empresa_id> (role_required('gestor','gestor_dono','cliente'), empresa_required, query Lead where empresa_id=param filtered by status query param if present, paginate 25/page, render list template). POST /leads/<lead_id>/status (validate empresa_required on lead.empresa_id, validate state transition, if novo_status='contrato' require valor_contrato > 0, update lead, call auditoria.registrar_acao with dados_anteriores={status: old, valor: old} and dados_novos={status: new, valor: new}, redirect back with flash)
- [ ] T054 [P] [US3] Create `app/templates/leads/lista.html`: extends base.html, filter dropdown by status, table with columns: nome, telefone, origem_campanha, status (badge colored), valor_contrato, criado_em. Each row has "Alterar Status" button/dropdown. Pagination controls.
- [ ] T055 [P] [US3] Create `app/templates/leads/status_form.html`: modal or inline form for LeadStatusForm, conditional valor_contrato field (shown only when contrato selected via JS)
- [ ] T056 [US3] Create `tests/test_leads.py`: test status transition novo→orcamento succeeds, test orcamento→contrato requires valor_contrato > 0 (fail without, succeed with), test invalid transition contrato→novo fails, test status change creates LogAuditoria record with correct dados_anteriores/dados_novos, test cliente can only see leads of own empresa (403 for other), test gestor can only see leads of assigned empresa. Constitution Principle II & III coverage.

**Checkpoint**: Leads gerenciáveis por gestor e cliente. Log de auditoria registra toda mudança. Isolamento multi-tenant testado.

---

## Phase 7: User Story 4 — Gestor dono gerencia equipe (Priority: P2)

**Goal**: Gestor dono aprova/remove gestores e vê todos os clientes de todos os gestores.

**Independent Test**: Aprovar gestor pendente, verificar que ele consegue fazer login. Remover gestor, verificar acesso negado.

### Implementation for User Story 4

- [ ] T057 [US4] Add gestor management routes to `app/blueprints/gestor/routes.py`: GET /gestor/gestores (role_required('gestor_dono'), list all Usuario where perfil='gestor' with status and count of empresas), POST /gestor/gestores/<id>/aprovar (role_required('gestor_dono'), set usuario.status='ativo', registrar_acao), POST /gestor/gestores/<id>/remover (role_required('gestor_dono'), set usuario.status='inativo', set empresa.gestor_id=NULL for their empresas, registrar_acao)
- [ ] T058 [P] [US4] Create `app/templates/gestor/gestores.html`: extends base.html, table with gestores: nome, email, status (badge), qtd clientes. Buttons "Aprovar" (if pendente) and "Remover" (if ativo) with confirmation dialog.
- [ ] T059 [US4] Update `app/blueprints/gestor/routes.py` GET /gestor/clientes: if current_user.perfil == 'gestor_dono', show all empresas with optional filter by gestor. Add gestor name column to template.
- [ ] T060 [US4] Update `app/templates/gestor/clientes.html`: add gestor filter dropdown (visible only for gestor_dono), add gestor nome column

**Checkpoint**: Gestor dono tem visão completa de equipe e clientes. Aprovação/remoção funcional.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Refinamentos que afetam múltiplas user stories

- [ ] T061 [P] Add flash messages styling to `app/templates/base.html`: success (green), error (red), info (blue) with Tailwind classes, auto-dismiss after 5s
- [ ] T062 [P] Create `app/templates/errors/403.html` and `app/templates/errors/404.html`: error pages in pt-BR with link to home
- [ ] T063 Register error handlers in `app/__init__.py`: 403 → render 403.html, 404 → render 404.html
- [ ] T064 [P] Add empty state templates: `app/templates/cliente/painel_vazio.html` (message "Nenhum dado disponível para o período selecionado"), used in painel route when no MetricaDiaria exists
- [ ] T065 [P] Add Metabase locale configuration to `docker-compose.yml`: MB_SITE_LOCALE=pt for pt-BR interface
- [ ] T066 [P] Create `railway.toml` with build and deploy config: [build] builder=dockerfile, [deploy] numReplicas=1, healthcheckPath=/login. Add cron schedule for sync: `flask sync-metricas` every hour.
- [ ] T067 Update `app/services/sync_metricas.py`: add structured logging (logger.info/error) for each empresa sync — log empresa_id, metricas count, duration, errors. NEVER log tokens.
- [ ] T068 Run `ruff check .` and `ruff format .` across entire codebase, fix all issues
- [ ] T069 Run full quickstart.md validation scenarios V1–V8 and verify all pass
- [ ] T070 Run `pytest -v` and verify all tests pass: test_auth, test_permissoes, test_crypto, test_leads, test_sync

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Phase 2 — first story to implement
- **US5 (Phase 4)**: Depends on Phase 3 (needs ContaAnuncio model and meta_ads service)
- **US2 (Phase 5)**: Depends on Phase 4 (needs MetricaDiaria data for dashboard)
- **US3 (Phase 6)**: Depends on Phase 2 only — can run in parallel with US1/US5/US2
- **US4 (Phase 7)**: Depends on Phase 2 only — can run in parallel with US1/US5/US2
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

```
Phase 2 (Foundational)
  ├── US1 (Phase 3): Cadastro + Meta OAuth
  │     └── US5 (Phase 4): Sincronização
  │           └── US2 (Phase 5): Painel + PDF
  ├── US3 (Phase 6): Leads (independent)
  └── US4 (Phase 7): Gestão gestores (independent)
```

- **US1 → US5 → US2**: Cadeia sequencial (cada um precisa do anterior)
- **US3**: Independente — pode ser feita em paralelo com US1/US5/US2
- **US4**: Independente — pode ser feita em paralelo com qualquer outra

### Within Each User Story

- Models before services
- Services before routes
- Routes before templates
- Core implementation before integration
- Tests validate the story

### Parallel Opportunities

**Phase 1** (all [P]):
- T003 (Dockerfile) + T004 (docker-compose) + T005 (.env.example) + T006 (.gitignore)

**Phase 2** (within phase):
- T012 (Empresa model) + T013 (LogAuditoria model) after T011
- T020 (base.html) + T021 (auth templates) after T019

**Phase 3 US1**:
- T033 (clientes.html) + T034 (cliente_form.html) + T035 (cliente_detalhe.html) after T031

**Phase 5 US2**:
- T047 (painel.html) + T048 (painel_pdf.html) after T045

**Cross-story parallel** (after Phase 2):
- US3 (Phase 6) can run entirely in parallel with US1→US5→US2 chain
- US4 (Phase 7) can run entirely in parallel with US1→US5→US2 chain

---

## Parallel Example: After Phase 2

```text
Developer A (main chain):        Developer B (independent):
├── Phase 3: US1 (cadastro+Meta)  ├── Phase 6: US3 (leads)
├── Phase 4: US5 (sync)           └── Phase 7: US4 (gestores)
└── Phase 5: US2 (painel+PDF)
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: US1 (cadastro + Meta)
4. **STOP and VALIDATE**: Gestor cadastra cliente e conecta Meta com sucesso
5. Deploy para Railway e testar com conta Meta real

### Incremental Delivery

1. Setup + Foundational → Base funcional
2. US1 → Gestor cadastra clientes e conecta Meta → Deploy (MVP!)
3. US5 → Métricas sincronizando automaticamente → Deploy
4. US2 → Painel visível para cliente com PDF → Deploy
5. US3 → Leads gerenciáveis → Deploy
6. US4 → Gestão de equipe → Deploy
7. Polish → Refinamentos e validação final → Deploy

### Parallel Team Strategy

With 2 developers after Phase 2:

1. Team completa Setup + Foundational juntos
2. Dev A: US1 → US5 → US2 (cadeia principal)
3. Dev B: US3 → US4 (stories independentes)
4. Ambos: Polish juntos

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Tests are included for permission rules and budget/verba rules (Constitution Principle VI mandatory)
- Metabase dashboards require one-time manual setup via Metabase UI (create questions + dashboard, configure embed) — not automated in tasks
- First client: empresa de fotografia de festas e casamentos (seed data in conftest.py fixtures)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
