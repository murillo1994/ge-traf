# Data Model: Portal de Relatórios de Tráfego Pago

**Date**: 2026-10-31

## Entity Relationship Overview

```
Usuario ──┬── pertence a ──▶ Empresa (via usuario_empresa ou empresa_id)
           └── tem perfil: gestor_dono | gestor | cliente

Empresa ──┬── tem muitas ──▶ ContaAnuncio
           ├── tem muitas ──▶ MetricaDiaria
           ├── tem muitos ──▶ Lead
           └── pertence a ──▶ Usuario (gestor_id)

ContaAnuncio ──── gera ──▶ MetricaDiaria

Lead ──── tem muitas ──▶ LogAuditoria

LogAuditoria ──── referencia ──▶ Usuario (autor da ação)
```

## Entities

### Usuario

| Campo | Tipo | Constraints | Notas |
|-------|------|-------------|-------|
| id | UUID | PK | |
| email | string(255) | UNIQUE, NOT NULL | Login |
| senha_hash | string(255) | NOT NULL | bcrypt hash |
| nome | string(150) | NOT NULL | |
| perfil | enum | NOT NULL | `gestor_dono`, `gestor`, `cliente` |
| status | enum | NOT NULL, default `pendente` | `pendente`, `ativo`, `inativo` |
| empresa_id | UUID | FK → Empresa, NULLABLE | Para perfil `cliente`: empresa vinculada |
| criado_em | datetime | NOT NULL, default now | |
| atualizado_em | datetime | NOT NULL, auto-update | |

**Validation rules**:
- Email DEVE ser único no sistema.
- Perfil `gestor_dono` DEVE existir no máximo 1 por instalação (MVP).
- Perfil `cliente` DEVE ter `empresa_id` preenchido.
- Perfil `gestor` pode gerenciar múltiplas empresas (via relação Empresa.gestor_id).
- Status `pendente` para novos gestores; gestor_dono aprova para `ativo`.

### Empresa

| Campo | Tipo | Constraints | Notas |
|-------|------|-------------|-------|
| id | UUID | PK | empresa_id usado como tenant filter |
| nome | string(200) | NOT NULL | |
| segmento | string(100) | NULLABLE | Ex: "Fotografia de festas" |
| teto_verba_mensal | decimal(12,2) | NULLABLE | Valor máximo de gasto/mês |
| gestor_id | UUID | FK → Usuario, NOT NULL | Gestor responsável |
| status_conexao | enum | NOT NULL, default `aguardando` | `aguardando`, `conectado`, `reconexao_necessaria` |
| criado_em | datetime | NOT NULL, default now | |
| atualizado_em | datetime | NOT NULL, auto-update | |

**Validation rules**:
- `gestor_id` DEVE referenciar um Usuario com perfil `gestor` ou `gestor_dono`.
- `teto_verba_mensal` quando preenchido DEVE ser > 0.
- Toda query que acessa Empresa DEVE filtrar pelo contexto do usuário logado.

### ContaAnuncio

| Campo | Tipo | Constraints | Notas |
|-------|------|-------------|-------|
| id | UUID | PK | |
| empresa_id | UUID | FK → Empresa, NOT NULL | Tenant filter |
| plataforma | enum | NOT NULL | `meta` (futuramente `google`) |
| conta_id_externo | string(100) | NOT NULL | Ad Account ID da plataforma |
| token_criptografado | binary | NOT NULL | Fernet-encrypted access token |
| token_expira_em | datetime | NULLABLE | Quando o token expira |
| status | enum | NOT NULL, default `ativo` | `ativo`, `expirado`, `revogado` |
| criado_em | datetime | NOT NULL, default now | |
| atualizado_em | datetime | NOT NULL, auto-update | |

**Validation rules**:
- `token_criptografado` NUNCA pode ser retornado em queries de API ou templates.
- Uma empresa pode ter no máximo 1 conta por plataforma (UNIQUE: empresa_id + plataforma).
- Quando `token_expira_em` < now, status muda para `expirado` na próxima sincronização.

### MetricaDiaria

| Campo | Tipo | Constraints | Notas |
|-------|------|-------------|-------|
| id | UUID | PK | |
| empresa_id | UUID | FK → Empresa, NOT NULL | Tenant filter |
| conta_anuncio_id | UUID | FK → ContaAnuncio, NOT NULL | |
| data | date | NOT NULL | Dia da métrica |
| campanha_id | string(100) | NOT NULL | ID da campanha na plataforma |
| campanha_nome | string(300) | NOT NULL | |
| conjunto_id | string(100) | NULLABLE | Ad Set ID |
| conjunto_nome | string(300) | NULLABLE | |
| anuncio_id | string(100) | NULLABLE | Ad ID |
| anuncio_nome | string(300) | NULLABLE | |
| impressoes | integer | NOT NULL, default 0 | Alcance/impressões |
| cliques | integer | NOT NULL, default 0 | |
| gasto | decimal(12,2) | NOT NULL, default 0 | Valor gasto no dia |
| leads_gerados | integer | NOT NULL, default 0 | |
| criativo_url | string(500) | NULLABLE | URL do thumbnail do criativo |
| criativo_titulo | string(300) | NULLABLE | |
| sincronizado_em | datetime | NOT NULL | Quando foi importado |

**Validation rules**:
- UNIQUE constraint em (empresa_id, data, anuncio_id) para evitar duplicatas.
- Toda query DEVE filtrar por `empresa_id`.
- Dados são insert-or-update (upsert) na sincronização.

### Lead

| Campo | Tipo | Constraints | Notas |
|-------|------|-------------|-------|
| id | UUID | PK | |
| empresa_id | UUID | FK → Empresa, NOT NULL | Tenant filter |
| nome | string(200) | NULLABLE | Nome do contato |
| telefone | string(50) | NULLABLE | |
| email | string(255) | NULLABLE | |
| origem_campanha | string(300) | NULLABLE | Nome da campanha de origem |
| origem_conjunto | string(300) | NULLABLE | Nome do ad set |
| origem_anuncio | string(300) | NULLABLE | Nome do anúncio |
| status | enum | NOT NULL, default `novo` | `novo`, `orcamento`, `contrato`, `perdido` |
| valor_contrato | decimal(12,2) | NULLABLE | Preenchido quando status = contrato |
| criado_em | datetime | NOT NULL, default now | |
| atualizado_em | datetime | NOT NULL, auto-update | |

**Validation rules**:
- `valor_contrato` DEVE ser preenchido quando status muda para `contrato`.
- `valor_contrato` DEVE ser > 0 quando preenchido.
- Toda mudança de `status` DEVE gerar um registro em LogAuditoria.

**State transitions**:
```
novo → orcamento → contrato
novo → orcamento → perdido
novo → perdido
orcamento → novo (reversão permitida)
```

### LogAuditoria

| Campo | Tipo | Constraints | Notas |
|-------|------|-------------|-------|
| id | UUID | PK | |
| empresa_id | UUID | FK → Empresa, NOT NULL | Tenant filter |
| usuario_id | UUID | FK → Usuario, NOT NULL | Quem fez a ação |
| acao | string(100) | NOT NULL | Ex: "lead_status_alterado", "conta_conectada" |
| entidade_tipo | string(50) | NOT NULL | Ex: "lead", "conta_anuncio" |
| entidade_id | UUID | NOT NULL | ID do registro afetado |
| dados_anteriores | JSON | NULLABLE | Estado antes da ação |
| dados_novos | JSON | NULLABLE | Estado depois da ação |
| criado_em | datetime | NOT NULL, default now | Timestamp imutável |

**Validation rules**:
- Tabela é APPEND-ONLY: sem UPDATE ou DELETE permitido.
- Toda query DEVE filtrar por `empresa_id`.
- `criado_em` NUNCA pode ser alterado após inserção.

## Indexes

| Tabela | Index | Tipo | Justificativa |
|--------|-------|------|---------------|
| MetricaDiaria | (empresa_id, data) | BTREE | Filtro principal do painel por período |
| MetricaDiaria | (empresa_id, data, anuncio_id) | UNIQUE | Previne duplicatas na sincronização |
| Lead | (empresa_id, status) | BTREE | Filtro de leads por status |
| Lead | (empresa_id, criado_em) | BTREE | Ordenação cronológica |
| LogAuditoria | (empresa_id, criado_em) | BTREE | Consulta de auditoria por período |
| Usuario | (email) | UNIQUE | Login |
| ContaAnuncio | (empresa_id, plataforma) | UNIQUE | Uma conta por plataforma por empresa |
