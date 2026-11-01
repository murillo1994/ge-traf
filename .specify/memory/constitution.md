<!--
## Sync Impact Report
- Version change: (none) → 1.0.0
- Modified principles: N/A (initial ratification)
- Added sections:
  - Core Principles (6 principles)
  - Technology Stack
  - Development Workflow
  - Governance
- Removed sections: N/A
- Follow-up TODOs: none
-->

# GeTraf Constitution

## Core Principles

### I. Stack Definida

- O projeto DEVE usar Python 3.11+, Flask, PostgreSQL e Tailwind CSS.
- Containerização via Docker é OBRIGATÓRIA para todos os ambientes.
- Deploy DEVE ser feito no Railway.
- Nenhuma dependência de framework ou runtime fora desta stack é permitida
  sem emenda à constituição.

### II. Isolamento Multi-Tenant

- Toda consulta ao banco de dados DEVE filtrar por `empresa_id`.
- Uma empresa NUNCA pode acessar, visualizar ou modificar dados de outra.
- Rotas, queries e APIs DEVEM validar `empresa_id` no nível de middleware
  ou decorator antes de qualquer operação de leitura ou escrita.
- Testes DEVEM cobrir cenários de vazamento cross-tenant como casos
  de falha obrigatórios.

### III. Aprovação Explícita para Ações Financeiras (NON-NEGOTIABLE)

- Nenhuma ação que envolva gasto de dinheiro (criar campanha, ativar
  campanha, aumentar verba) DEVE acontecer sem confirmação explícita
  de um usuário com perfil Gestor.
- Toda ação financeira DEVE ser registrada em log de auditoria contendo:
  usuário, timestamp, ação, valor envolvido e empresa_id.
- O log de auditoria é append-only; registros NUNCA podem ser editados
  ou removidos.

### IV. Segurança de Credenciais

- Tokens de Meta e Google DEVEM ser armazenados criptografados no banco
  de dados (encryption at rest).
- Tokens NUNCA podem aparecer em respostas de API, templates do front-end,
  logs de aplicação ou logs de erro.
- Descriptografia DEVE acontecer exclusivamente no momento do uso,
  no backend, em memória.

### V. Interface Acessível em Português

- Toda a interface DEVE ser em português do Brasil.
- O perfil Empresa DEVE ter interface simplificada, compreensível para
  usuários sem conhecimento técnico.
- Jargão técnico de tráfego pago DEVE ser acompanhado de explicações
  contextuais quando exibido para o perfil Empresa.

### VI. Qualidade de Código e Testes

- Testes DEVEM ser escritos com pytest.
- Regras de permissão e regras de verba DEVEM ter cobertura de testes
  obrigatória; PRs que alterem essas regras sem testes correspondentes
  DEVEM ser rejeitados.
- Todo código DEVE ser formatado com ruff antes do commit.
- Linting com ruff DEVE passar sem erros como pré-condição para merge.

## Technology Stack

- **Linguagem**: Python 3.11+
- **Framework Web**: Flask
- **Banco de Dados**: PostgreSQL
- **Frontend/CSS**: Tailwind CSS (templates Jinja2)
- **Containerização**: Docker + Docker Compose
- **Deploy**: Railway
- **Testes**: pytest
- **Linting/Formatting**: ruff
- **Integrações**: Meta Ads API, Google Ads API

## Development Workflow

- Todo PR DEVE passar por review antes do merge.
- O pipeline de CI DEVE executar: ruff check, ruff format --check, e
  pytest com cobertura mínima para módulos de permissão e verba.
- Migrations de banco DEVEM ser versionadas e reversíveis.
- Variáveis de ambiente sensíveis (tokens, database URL, secret keys)
  NUNCA podem ser commitadas no repositório; DEVEM usar variáveis de
  ambiente ou secret manager do Railway.
- Branches seguem o padrão: `feature/`, `fix/`, `chore/`.

## Governance

- Esta constituição é o documento autoritativo do projeto GeTraf.
  Em caso de conflito com outras práticas, a constituição prevalece.
- Emendas DEVEM ser documentadas com justificativa, aprovadas pelo
  responsável do projeto, e acompanhadas de plano de migração quando
  aplicável.
- Todo PR e review DEVE verificar conformidade com os princípios aqui
  definidos.
- Versionamento segue Semantic Versioning: MAJOR para remoções ou
  redefinições de princípios, MINOR para adições, PATCH para
  clarificações.

**Version**: 1.0.0 | **Ratified**: 2026-10-31 | **Last Amended**: 2026-10-31
