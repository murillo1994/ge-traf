"""
Script para configurar o Metabase automaticamente via API.
Roda depois que o Metabase estiver acessível (docker compose up).

Uso:
    python deploy/setup-metabase.py

O que faz:
    1. Cria o usuário admin no Metabase
    2. Conecta ao banco PostgreSQL do GeTraf
    3. Ativa embedding e gera a secret key
    4. Imprime a METABASE_SECRET_KEY para colocar no .env
"""

import os
import sys
import time

import requests

METABASE_URL = os.environ.get("METABASE_URL", "http://localhost:3000")
ADMIN_EMAIL = os.environ.get("METABASE_ADMIN_EMAIL", "admin@getraf.com")
ADMIN_PASSWORD = os.environ.get("METABASE_ADMIN_PASSWORD", "GeTraf@2024!")


def wait_for_metabase():
    print("Aguardando Metabase iniciar...")
    for i in range(60):
        try:
            r = requests.get(f"{METABASE_URL}/api/health", timeout=5)
            if r.status_code == 200 and r.json().get("status") == "ok":
                print("Metabase pronto!")
                return True
        except requests.ConnectionError:
            pass
        time.sleep(5)
    print("Timeout aguardando Metabase.")
    return False


def setup_admin():
    print("Verificando setup inicial...")
    r = requests.get(f"{METABASE_URL}/api/session/properties")
    props = r.json()

    if props.get("setup-token"):
        token = props["setup-token"]
        print("Criando usuário admin...")
        r = requests.post(
            f"{METABASE_URL}/api/setup",
            json={
                "token": token,
                "user": {
                    "email": ADMIN_EMAIL,
                    "password": ADMIN_PASSWORD,
                    "first_name": "Admin",
                    "last_name": "GeTraf",
                    "site_name": "GeTraf",
                },
                "prefs": {
                    "site_name": "GeTraf",
                    "site_locale": "pt",
                    "allow_tracking": False,
                },
            },
        )
        if r.status_code == 200:
            print(f"Admin criado: {ADMIN_EMAIL}")
            return r.json().get("id")
        else:
            print(f"Erro ao criar admin: {r.text}")
            return None
    else:
        print("Metabase já configurado, fazendo login...")
        return login()


def login():
    r = requests.post(
        f"{METABASE_URL}/api/session",
        json={
            "username": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD,
        },
    )
    if r.status_code == 200:
        return r.json()["id"]
    print(f"Erro no login: {r.text}")
    return None


def add_database(session_id):
    headers = {"X-Metabase-Session": session_id}

    r = requests.get(f"{METABASE_URL}/api/database", headers=headers)
    databases = r.json().get("data", [])
    for db in databases:
        if db.get("name") == "GeTraf":
            print("Banco GeTraf já conectado no Metabase.")
            return db["id"]

    print("Conectando banco GeTraf ao Metabase...")
    r = requests.post(
        f"{METABASE_URL}/api/database",
        headers=headers,
        json={
            "engine": "postgres",
            "name": "GeTraf",
            "details": {
                "host": "postgres",
                "port": 5432,
                "dbname": "getraf",
                "user": "getraf",
                "password": "getraf",
                "ssl": False,
            },
        },
    )
    if r.status_code == 200:
        db_id = r.json()["id"]
        print(f"Banco conectado (ID: {db_id})")
        return db_id
    else:
        print(f"Erro ao conectar banco: {r.text}")
        return None


def enable_embedding(session_id):
    headers = {"X-Metabase-Session": session_id}

    print("Ativando embedding...")
    requests.put(
        f"{METABASE_URL}/api/setting/enable-embedding",
        headers=headers,
        json={"value": True},
    )

    r = requests.get(
        f"{METABASE_URL}/api/setting/embedding-secret-key", headers=headers
    )
    secret = r.json()
    if secret:
        print(f"\n{'=' * 60}")
        print(f"METABASE_SECRET_KEY={secret}")
        print(f"{'=' * 60}")
        print("\nCopie esta chave para o seu .env")
        return secret
    else:
        print("Erro ao obter embedding secret key")
        return None


def main():
    if not wait_for_metabase():
        sys.exit(1)

    session_id = setup_admin()
    if not session_id:
        sys.exit(1)

    if not isinstance(session_id, str):
        session_id = login()

    add_database(session_id)
    enable_embedding(session_id)

    print("\n=== Metabase configurado! ===")
    print(f"Acesse: {METABASE_URL}")
    print(f"Login: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
    print("\nPróximos passos:")
    print("  1. Copie a METABASE_SECRET_KEY para o .env")
    print("  2. Crie o dashboard com os 6 widgets no Metabase")
    print("  3. Anote o ID do dashboard e coloque em METABASE_DASHBOARD_ID no .env")
    print("  4. Reinicie o portal: docker compose restart portal")


if __name__ == "__main__":
    main()
