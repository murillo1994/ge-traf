#!/bin/bash
set -e

echo "Aguardando PostgreSQL..."
while ! python -c "import socket; s=socket.socket(); s.connect(('postgres',5432)); s.close()" 2>/dev/null; do
    sleep 1
done
echo "PostgreSQL disponível."

echo "Rodando migrations..."
flask db upgrade

exec "$@"
