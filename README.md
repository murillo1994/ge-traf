# GeTraf - Gestão de Tráfego

Portal web de relatórios de tráfego pago para gestores de tráfego e seus clientes.

## Sobre

O GeTraf automatiza a coleta e apresentação de métricas de campanhas de anúncios (Meta Ads), eliminando a necessidade de montar relatórios manuais. Gestores cadastram clientes, conectam contas de anúncio, e os dados são sincronizados automaticamente a cada hora.

## Funcionalidades

- **Painel de métricas** — Investido x contratos, funil de conversão, CPL/CPC, ranking de criativos, verba x teto, origem dos leads
- **Gestão de leads** — Lista com status (novo → orçamento → contrato / perdido), valor do contrato, log de auditoria
- **Integração Meta Ads** — OAuth, coleta automática via facebook-business SDK
- **Multi-tenant** — Isolamento por `empresa_id` em todas as queries
- **Dashboards Metabase** — Embed com JWT assinado e filtro travado por empresa
- **Export PDF** — Relatórios via WeasyPrint
- **3 perfis de acesso** — Gestor dono, gestor, cliente

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python 3.11+, Flask 3.x, SQLAlchemy 2.x |
| Banco de dados | PostgreSQL 16 |
| Fila de jobs | RQ + Redis |
| Dashboards | Metabase OSS (embedded) |
| Frontend | Jinja2 + Tailwind CSS |
| Segurança | Fernet (tokens), bcrypt (senhas), Flask-Login |
| Infra | Docker Compose, Railway |

## Estrutura do Projeto

```
app/
├── blueprints/
│   ├── auth/          # Login, registro, logout
│   ├── gestor/        # CRUD clientes, OAuth Meta, gestão de gestores
│   ├── cliente/       # Painel de métricas, export PDF
│   └── leads/         # Lista e transição de status dos leads
├── models/            # Usuario, Empresa, Lead, ContaAnuncio, MetricaDiaria, LogAuditoria
├── services/          # crypto, auditoria, meta_ads, sync_metricas, metabase_embed, pdf_export
└── templates/         # Jinja2 templates (pt-BR)
tests/                 # 25 testes (auth, permissões, crypto, leads, sync)
specs/                 # Especificações via spec-kit
```

## Requisitos

- Python 3.11+
- PostgreSQL 16
- Redis
- Docker e Docker Compose (para deploy completo)

## Setup Local

```bash
# Clonar o repositório
git clone https://github.com/murillo1994/ge-traf.git
cd ge-traf

# Criar e ativar ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas credenciais

# Inicializar banco de dados
flask db init
flask db migrate -m "initial"
flask db upgrade

# Criar primeiro gestor dono
flask create-owner

# Rodar servidor de desenvolvimento
flask run
```

## Docker Compose

```bash
# Subir todos os serviços (portal, postgres, redis, metabase, worker)
docker compose up -d

# Criar gestor dono no container
docker compose exec portal flask create-owner
```

### Serviços

| Serviço | Porta | Descrição |
|---------|-------|-----------|
| portal | 5000 | Aplicação Flask |
| postgres | 5432 | Banco de dados |
| redis | 6379 | Fila de jobs |
| metabase | 3000 | Dashboards |
| worker | — | Processamento de jobs RQ |

## Variáveis de Ambiente

Veja o arquivo [.env.example](.env.example) para a lista completa. As principais:

| Variável | Descrição |
|----------|-----------|
| `SECRET_KEY` | Chave secreta do Flask |
| `DATABASE_URL` | URL de conexão PostgreSQL |
| `FERNET_KEY` | Chave de criptografia para tokens de anúncio |
| `META_APP_ID` | App ID do Meta for Developers |
| `META_APP_SECRET` | App Secret do Meta |
| `METABASE_SECRET_KEY` | Chave para embed assinado do Metabase |
| `REDIS_URL` | URL de conexão Redis |

## Testes

```bash
# Rodar todos os 25 testes
python -m pytest tests/ -v

# Lint e formatação
python -m ruff check .
python -m ruff format .
```

### Cobertura dos testes

- **Auth** — Login, logout, registro, duplicata de email
- **Permissões** — Isolamento multi-tenant, restrição por perfil, redirecionamento sem auth
- **Crypto** — Encrypt/decrypt Fernet, chave errada falha
- **Leads** — Transições de status, valor obrigatório para contrato, log de auditoria
- **Sync** — Criação de métricas, token expirado marca reconexão, upsert sem duplicatas

## Deploy na VPS (Hostinger)

```bash
# Na VPS, rode:
curl -fsSL https://raw.githubusercontent.com/murillo1994/ge-traf/master/deploy/setup-vps.sh | bash

# Criar gestor dono
cd /opt/getraf
docker compose exec portal flask create-owner

# Configurar Metabase
pip3 install requests
python3 deploy/setup-metabase.py
# Copie a METABASE_SECRET_KEY para o .env

# Configurar Nginx + SSL
sudo apt install nginx certbot python3-certbot-nginx
sudo cp deploy/nginx.conf /etc/nginx/sites-available/getraf
sudo ln -s /etc/nginx/sites-available/getraf /etc/nginx/sites-enabled/
# Edite o domínio no arquivo e rode:
sudo certbot --nginx -d SEU-DOMINIO.com.br
sudo systemctl reload nginx
```

### Metabase Dashboard

Após o setup, crie o dashboard no Metabase (http://localhost:3000) com as 6 queries em `deploy/metabase-dashboard-queries.sql`. Cada query usa `{{empresa_id}}` como filtro, travado via JWT no embed assinado.

## Segurança

- Tokens de Meta/Google criptografados com Fernet (nunca expostos no frontend ou logs)
- Senhas com hash bcrypt
- Isolamento multi-tenant: toda query filtra por `empresa_id`
- Log de auditoria append-only para ações financeiras e de leads
- CSRF protection via Flask-WTF

## Licença

Projeto privado. Todos os direitos reservados.
