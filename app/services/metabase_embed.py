import os
from datetime import UTC

import jwt


def generate_embed_url(dashboard_id, empresa_id, params=None):
    secret_key = os.environ.get("METABASE_SECRET_KEY", "")
    site_url = os.environ.get("METABASE_SITE_URL", "http://localhost:3000")

    payload = {
        "resource": {"dashboard": int(dashboard_id)},
        "params": {"empresa_id": str(empresa_id)},
        "exp": _expiration(),
    }
    if params:
        payload["params"].update(params)

    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return f"{site_url}/embed/dashboard/{token}#bordered=false&titled=false"


def _expiration():
    from datetime import datetime, timedelta

    return int((datetime.now(UTC) + timedelta(hours=1)).timestamp())
