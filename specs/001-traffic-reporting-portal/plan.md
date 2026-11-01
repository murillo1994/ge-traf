# Implementation Plan: Portal de Relatórios de Tráfego Pago

**Branch**: `001-traffic-reporting-portal` | **Date**: 2026-10-31 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-traffic-reporting-portal/spec.md`

## Summary

Portal web multi-tenant de relatórios de tráfego pago. Gestores cadastram clientes e conectam contas Meta Ads via OAuth; um job horário (RQ + Redis) sincroniza métricas usando o SDK facebook-business. Dashboards são servidos via Metabase embeddado (guest embed com filtro empresa_id travado por token JWT assinado pelo Flask). Gestão de leads com funil de status e log de auditoria append-only. Stack: Flask (Blueprints) + SQLAlchemy/Alembic + PostgreSQL + Jinja/Tailwind + Docker no Railway.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Flask 3.x, Flask-Login, SQLAlchemy 2.x, Alembic, RQ (Redis Queue), facebook-business SDK, cryptography (Fernet), PyJWT (Metabase embed tokens), WeasyPrint (PDF export)

**Storage**: PostgreSQL 16 (via SQLAlchemy ORM + Alembic migrations)

**Cache/Queue**: Redis 7 (broker para RQ worker)

**Dashboards**: Metabase OSS (Docker container, guest embed)

**Testing**: pytest + ruff (lint/format)

**Target Platform**: Linux containers (Docker) no Railway

**Project Type**: Web application (server-rendered com Jinja2 + Tailwind)

**Performance Goals**: Painel carrega em < 3s; sincronização horária completa em < 10 min para 50 clientes

**Constraints**: Tokens criptografados (Fernet); isolamento multi-tenant por empresa_id em toda query; interface 100% pt-BR

**Scale/Scope**: MVP para 1 gestor dono, ~5 gestores, ~50 clientes. Primeiro cliente: empresa de fotografia de festas e casamentos.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Status | Notas |
|-----------|--------|-------|
| I. Stack Definida (Python/Flask/PostgreSQL/Tailwind/Docker/Railway) | PASS | Stack proposta alinhada 100% |
| II. Isolamento Multi-Tenant (empresa_id em toda query) | PASS | SQLAlchemy query filters + Metabase embed com filtro travado |
| III. Aprovação Explícita para Ações Financeiras | PASS | MVP é somente leitura; não cria/altera campanhas. Leads com log de auditoria |
| IV. Segurança de Credenciais (Fernet, nunca no front/logs) | PASS | Fernet encryption at rest; descriptografia só no backend no momento do uso |
| V. Interface Acessível em Português | PASS | Jinja templates 100% pt-BR; Metabase embed configurado em pt-BR |
| VI. Qualidade de Código e Testes (pytest + ruff) | PASS | pytest para permissão/verba; ruff no CI |

**Gate result**: ALL PASS — nenhuma violação.

## Project Structure

### Documentation (this feature)

```text
specs/001-traffic-reporting-portal/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── routes.md
└── tasks.md            # (gerado por /speckit-tasks)
```

### Source Code (repository root)

```text
app/
├── __init__.py          # create_app factory
├── config.py            # Config classes (dev/prod/test)
├── extensions.py        # db, login_manager, migrate, fernet
├── models/
│   ├── __init__.py
│   ├── usuario.py       # User model (Flask-Login)
│   ├── empresa.py       # Empresa (cliente/tenant)
│   ├── conta_anuncio.py # Conta de anúncio (Meta OAuth)
│   ├── metrica_diaria.py# Métricas sincronizadas
│   ├── lead.py          # Leads com status e valor
│   └── log_auditoria.py # Log append-only
├── blueprints/
│   ├── __init__.py
│   ├── auth/            # Login, logout, registro
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── forms.py
│   ├── gestor/          # CRUD clientes, conexão Meta, admin gestores
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── forms.py
│   ├── cliente/         # Painel, exportação PDF
│   │   ├── __init__.py
│   │   └── routes.py
│   └── leads/           # Lista e gestão de leads
│       ├── __init__.py
│       ├── routes.py
│       └── forms.py
├── services/            # Camada de serviço (preparada para IA Fase 2)
│   ├── __init__.py
│   ├── meta_ads.py      # facebook-business SDK wrapper
│   ├── sync_metricas.py # Job de sincronização (RQ task)
│   ├── metabase_embed.py# Geração de JWT para embed
│   ├── crypto.py        # Fernet encrypt/decrypt de tokens
│   ├── auditoria.py     # Registro de log append-only
│   └── pdf_export.py    # Geração de PDF (WeasyPrint)
├── decorators.py        # role_required, empresa_required
├── templates/
│   ├── base.html        # Layout base com Tailwind
│   ├── auth/
│   ├── gestor/
│   ├── cliente/
│   └── leads/
└── static/
    └── css/

tests/
├── conftest.py          # Fixtures (app, db, users por perfil)
├── test_auth.py
├── test_permissoes.py   # Isolamento cross-tenant, perfis
├── test_leads.py        # Status transitions, auditoria
├── test_sync.py         # Job de sincronização
└── test_crypto.py       # Fernet encrypt/decrypt

docker-compose.yml       # portal, postgres, redis, metabase
Dockerfile
requirements.txt
.env.example
```

**Structure Decision**: Aplicação Flask monolítica com Blueprints (auth, gestor, cliente, leads). Camada de services separada dos blueprints para lógica de negócio reutilizável e preparada para extensão com IA na Fase 2. Modelos SQLAlchemy em arquivos separados por entidade.

## Complexity Tracking

Nenhuma violação de constituição — seção não aplicável.
