# Quickstart Validation Guide

**Date**: 2026-10-31
**Feature**: Portal de Relatórios de Tráfego Pago

## Prerequisites

- Docker e Docker Compose instalados
- Conta de desenvolvedor Meta (Facebook for Developers) com App criado
- Variáveis de ambiente configuradas (ver `.env.example`)

## Setup

```bash
# 1. Clonar e configurar
cp .env.example .env
# Editar .env com:
#   SECRET_KEY, DATABASE_URL, REDIS_URL
#   META_APP_ID, META_APP_SECRET
#   FERNET_KEY (gerar: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
#   METABASE_SECRET_KEY, METABASE_SITE_URL

# 2. Subir os serviços
docker-compose up -d

# 3. Rodar migrations
docker-compose exec portal flask db upgrade

# 4. Criar gestor dono inicial
docker-compose exec portal flask create-owner --email admin@getraf.com --nome "Admin"
```

## Validation Scenarios

### V1: Autenticação e perfis (FR-001, US-6)

```bash
# 1. Acessar http://localhost:5000/login
# 2. Fazer login como gestor dono (admin@getraf.com)
# 3. Verificar redirect para /gestor/clientes
# 4. Acessar /gestor/gestores — deve listar apenas o dono
```

**Expected**: Login funciona; rotas de gestor acessíveis; rotas de cliente retornam 403.

### V2: Cadastro de cliente e conexão Meta (FR-003, FR-004, US-1)

```bash
# 1. Logado como gestor, acessar /gestor/clientes/novo
# 2. Preencher: nome="Fotografia Eventos", segmento="Fotografia", teto=5000
# 3. Submeter — verificar redirect e flash "Cliente cadastrado"
# 4. Na lista, clicar "Conectar Meta" no cliente criado
# 5. Autorizar no Facebook OAuth
# 6. Verificar redirect com flash "Conta Meta conectada"
```

**Expected**: Cliente criado com status `aguardando` → após OAuth, status `conectado`. Token armazenado criptografado (verificar no banco que `token_criptografado` não é legível).

### V3: Sincronização de métricas (FR-005, US-5)

```bash
# 1. Com cliente conectado, disparar job manualmente:
docker-compose exec portal flask sync-metricas

# 2. Verificar no banco:
docker-compose exec postgres psql -U getraf -c \
  "SELECT COUNT(*) FROM metrica_diaria WHERE empresa_id = '<id>';"
```

**Expected**: Métricas importadas para o cliente. Sem erros no log. Se token inválido, status da empresa muda para `reconexao_necessaria`.

### V4: Painel do cliente com Metabase embed (FR-006, FR-007, US-2)

```bash
# 1. Fazer login como cliente (user vinculado à empresa de fotografia)
# 2. Acessar /cliente/painel
# 3. Verificar: iframe Metabase carrega com 6 widgets
# 4. Alterar período para "últimos 7 dias"
# 5. Verificar que widgets atualizam
```

**Expected**: Dashboard Metabase renderiza dentro do portal. Filtro `empresa_id` travado (cliente não consegue ver dados de outra empresa). Seletor de período funciona.

### V5: Gestão de leads (FR-009, FR-010, FR-011, US-3)

```bash
# 1. Logado como gestor, acessar /leads/<empresa_id>
# 2. Verificar lista de leads com status "novo"
# 3. Alterar status de um lead para "orcamento"
# 4. Alterar outro para "contrato", informar valor R$ 3.500
# 5. Verificar log de auditoria no banco:
docker-compose exec postgres psql -U getraf -c \
  "SELECT * FROM log_auditoria WHERE entidade_tipo = 'lead' ORDER BY criado_em DESC LIMIT 5;"
```

**Expected**: Status atualizado. Valor salvo. Log de auditoria contém ambas as ações com dados_anteriores e dados_novos.

### V6: Isolamento multi-tenant (FR-012, SC-005)

```bash
# 1. Criar segundo cliente (empresa B) com gestor
# 2. Fazer login como cliente da empresa A
# 3. Tentar acessar /leads/<empresa_B_id> — deve retornar 403
# 4. Verificar que /cliente/painel mostra apenas dados da empresa A
```

**Expected**: Zero vazamento cross-tenant. Acesso negado para recursos de outra empresa.

### V7: Exportação PDF (FR-008, SC-004)

```bash
# 1. Logado como cliente, no painel selecionar período "último mês"
# 2. Clicar "Exportar PDF"
# 3. Verificar download do arquivo PDF
# 4. Abrir PDF e conferir os 6 widgets com dados corretos
```

**Expected**: PDF gerado com todos os widgets, dados corretos para o período, em português.

### V8: Gestão de gestores pelo dono (FR-002, US-4)

```bash
# 1. Registrar novo gestor via /registro
# 2. Logado como gestor dono, acessar /gestor/gestores
# 3. Verificar gestor com status "pendente"
# 4. Aprovar gestor
# 5. Fazer login como novo gestor — verificar acesso permitido
# 6. Voltar como dono, remover o gestor
# 7. Tentar login como gestor removido — verificar acesso negado
```

**Expected**: Fluxo completo de aprovação/remoção funciona. Gestor removido perde acesso.

## Running Tests

```bash
# Unit + integration tests
docker-compose exec portal pytest -v

# Apenas testes de permissão (críticos pela constituição)
docker-compose exec portal pytest tests/test_permissoes.py -v

# Lint check
docker-compose exec portal ruff check .
docker-compose exec portal ruff format --check .
```

## Constitution Compliance Checks

| Princípio | Como validar |
|-----------|-------------|
| II. Multi-tenant | V6 — tentar acessar dados de outra empresa |
| III. Aprovação financeira | MVP é read-only; verificar que não há rotas de criação de campanha |
| IV. Segurança de credenciais | V2 — verificar que token no banco é binário criptografado |
| V. Interface pt-BR | V4 — todos os textos em português |
| VI. Testes + ruff | Running Tests — pytest e ruff passam |
