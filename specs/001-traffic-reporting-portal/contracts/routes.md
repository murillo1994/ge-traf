# Route Contracts: Portal de Relatórios de Tráfego Pago

**Date**: 2026-10-31

## Blueprint: auth

| Método | Rota | Perfis | Descrição |
|--------|------|--------|-----------|
| GET | `/login` | público | Exibe formulário de login |
| POST | `/login` | público | Autentica usuário (email + senha) |
| GET | `/logout` | autenticado | Encerra sessão |
| GET | `/registro` | público | Formulário de registro (gestor) |
| POST | `/registro` | público | Cria usuário com status `pendente` |

### POST /login

**Request** (form):
- `email`: string, required
- `senha`: string, required

**Success**: Redirect para painel conforme perfil (gestor → /gestor/clientes, cliente → /cliente/painel)
**Failure**: Re-render formulário com mensagem de erro

### POST /registro

**Request** (form):
- `nome`: string, required
- `email`: string, required, unique
- `senha`: string, required, min 8 chars
- `confirmar_senha`: string, must match

**Success**: Redirect para /login com mensagem "Cadastro realizado. Aguarde aprovação."
**Failure**: Re-render com erros de validação

---

## Blueprint: gestor

**Acesso**: perfil `gestor` ou `gestor_dono`

| Método | Rota | Perfis | Descrição |
|--------|------|--------|-----------|
| GET | `/gestor/clientes` | gestor, gestor_dono | Lista clientes do gestor (dono vê todos) |
| GET | `/gestor/clientes/novo` | gestor, gestor_dono | Formulário de cadastro de cliente |
| POST | `/gestor/clientes/novo` | gestor, gestor_dono | Cria cliente |
| GET | `/gestor/clientes/<id>` | gestor, gestor_dono | Detalhes do cliente |
| GET | `/gestor/clientes/<id>/conectar-meta` | gestor, gestor_dono | Inicia OAuth Meta |
| GET | `/gestor/clientes/<id>/meta-callback` | gestor, gestor_dono | Callback OAuth Meta |
| GET | `/gestor/gestores` | gestor_dono | Lista gestores |
| POST | `/gestor/gestores/<id>/aprovar` | gestor_dono | Aprova gestor pendente |
| POST | `/gestor/gestores/<id>/remover` | gestor_dono | Remove gestor |

### POST /gestor/clientes/novo

**Request** (form):
- `nome`: string, required
- `segmento`: string, optional
- `teto_verba_mensal`: decimal, optional, > 0

**Success**: Redirect para /gestor/clientes com flash "Cliente cadastrado"
**Side effects**: Empresa criada com gestor_id = current_user.id, status_conexao = `aguardando`

### GET /gestor/clientes/<id>/conectar-meta

**Precondition**: Cliente pertence ao gestor logado (ou gestor_dono)
**Action**: Redirect para Facebook OAuth dialog com scopes `ads_read`, `ads_management`
**Failure**: 403 se cliente não pertence ao gestor

### GET /gestor/clientes/<id>/meta-callback

**Request** (query params from Meta OAuth):
- `code`: string (authorization code)

**Action**: Troca code por access token, criptografa com Fernet, salva em ContaAnuncio
**Success**: Redirect para /gestor/clientes/<id> com flash "Conta Meta conectada"
**Side effects**: Empresa.status_conexao → `conectado`; LogAuditoria registrado

---

## Blueprint: cliente

**Acesso**: perfil `cliente` (vê apenas sua empresa)

| Método | Rota | Perfis | Descrição |
|--------|------|--------|-----------|
| GET | `/cliente/painel` | cliente | Painel com dashboards Metabase embeddados |
| GET | `/cliente/painel/pdf` | cliente | Exporta painel em PDF |

### GET /cliente/painel

**Action**: Gera JWT Metabase com `empresa_id` locked → render iframe embed
**Query params** (optional):
- `periodo_inicio`: date (ISO), default: 30 dias atrás
- `periodo_fim`: date (ISO), default: hoje

**Response**: HTML com iframe Metabase + seletor de período

### GET /cliente/painel/pdf

**Query params**:
- `periodo_inicio`: date, required
- `periodo_fim`: date, required

**Response**: PDF download (Content-Disposition: attachment)
**Action**: Renderiza template PDF-specific com dados do banco via WeasyPrint

---

## Blueprint: leads

**Acesso**: `gestor`, `gestor_dono` (todos os clientes atribuídos), `cliente` (apenas seus leads)

| Método | Rota | Perfis | Descrição |
|--------|------|--------|-----------|
| GET | `/leads/<empresa_id>` | gestor, gestor_dono, cliente | Lista leads com filtros |
| POST | `/leads/<lead_id>/status` | gestor, gestor_dono, cliente | Atualiza status do lead |

### GET /leads/<empresa_id>

**Precondition**: Usuário tem acesso à empresa (seu cliente ou sua própria empresa)
**Query params** (optional):
- `status`: enum filter
- `pagina`: integer, default 1
- `por_pagina`: integer, default 25

**Response**: HTML com tabela de leads, filtros de status, paginação

### POST /leads/<lead_id>/status

**Request** (form):
- `novo_status`: enum, required (`novo`, `orcamento`, `contrato`, `perdido`)
- `valor_contrato`: decimal, required when novo_status = `contrato`

**Precondition**: Lead pertence a empresa acessível pelo usuário
**Success**: Redirect back com flash "Status atualizado"
**Side effects**: LogAuditoria criado com dados_anteriores e dados_novos

---

## Acesso por perfil — resumo

| Rota | gestor_dono | gestor | cliente |
|------|:-----------:|:------:|:-------:|
| /gestor/clientes | todos | seus clientes | — |
| /gestor/gestores | sim | — | — |
| /cliente/painel | — | — | sua empresa |
| /leads/<empresa_id> | qualquer | seus clientes | sua empresa |

O gestor_dono também pode acessar /cliente/painel passando empresa_id via query param (para visualizar o painel de qualquer cliente).
