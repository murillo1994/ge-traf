#!/bin/bash
set -e

echo "Aguardando PostgreSQL..."
while ! python -c "
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect(('postgres', 5432))
    s.close()
    exit(0)
except:
    exit(1)
" 2>/dev/null; do
    sleep 1
done
echo "PostgreSQL disponível."

echo "Rodando migrations..."
flask db upgrade

exec "$@"
