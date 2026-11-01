#!/bin/bash
set -e

echo "=== Setup GeTraf na VPS ==="

# 1. Instalar Docker e Docker Compose (se não existir)
if ! command -v docker &> /dev/null; then
    echo "Instalando Docker..."
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker $USER
    echo "Docker instalado. Faça logout e login novamente para usar sem sudo."
fi

if ! docker compose version &> /dev/null; then
    echo "Docker Compose já incluído no Docker Engine."
fi

# 2. Clonar repositório
APP_DIR="/opt/getraf"
if [ ! -d "$APP_DIR" ]; then
    echo "Clonando repositório..."
    sudo mkdir -p "$APP_DIR"
    sudo chown $USER:$USER "$APP_DIR"
    git clone https://github.com/murillo1994/ge-traf.git "$APP_DIR"
else
    echo "Atualizando repositório..."
    cd "$APP_DIR"
    git pull origin master
fi

cd "$APP_DIR"

# 3. Criar .env se não existir
if [ ! -f .env ]; then
    echo "Gerando .env com chaves seguras..."
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    FERNET_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")

    cat > .env <<EOF
FLASK_APP=wsgi.py
FLASK_CONFIG=production
SECRET_KEY=${SECRET_KEY}

DATABASE_URL=postgresql://getraf:getraf@postgres:5432/getraf
REDIS_URL=redis://redis:6379/0

FERNET_KEY=${FERNET_KEY}

META_APP_ID=
META_APP_SECRET=
META_REDIRECT_URI=https://SEU-DOMINIO/gestor/clientes/{id}/meta-callback

METABASE_SECRET_KEY=
METABASE_SITE_URL=http://metabase:3000
METABASE_DASHBOARD_ID=1
EOF
    echo ".env criado. Edite META_APP_ID, META_APP_SECRET e o domínio."
else
    echo ".env já existe, mantendo."
fi

# 4. Subir serviços
echo "Construindo e subindo serviços..."
docker compose up -d --build

echo ""
echo "=== Setup concluído ==="
echo "Portal:   http://localhost:5000"
echo "Metabase: http://localhost:3000"
echo ""
echo "Próximos passos:"
echo "  1. Criar gestor dono: docker compose exec portal flask create-owner"
echo "  2. Configurar Metabase em http://localhost:3000"
echo "  3. Editar .env com META_APP_ID e META_APP_SECRET"
echo "  4. Configurar Nginx como proxy reverso (ver deploy/nginx.conf)"
