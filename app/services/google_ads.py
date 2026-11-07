import logging
import os
from urllib.parse import quote, urlencode

logger = logging.getLogger(__name__)

GOOGLE_ADS_SCOPES = "https://www.googleapis.com/auth/adwords"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_ADS_API_VERSION = "v17"


def get_oauth_url(redirect_uri, state=None):
    client_id = os.environ.get("GOOGLE_ADS_CLIENT_ID")
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": GOOGLE_ADS_SCOPES,
        "response_type": "code",
        "access_type": "offline",
        "prompt": "consent",
    }
    if state:
        params["state"] = state
    return f"{GOOGLE_AUTH_URL}?{urlencode(params, quote_via=quote)}"


def exchange_code_for_token(code, redirect_uri):
    try:
        import requests

        client_id = os.environ.get("GOOGLE_ADS_CLIENT_ID")
        client_secret = os.environ.get("GOOGLE_ADS_CLIENT_SECRET")

        resp = requests.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()

        access_token = data["access_token"]
        refresh_token = data.get("refresh_token")

        customer_id = _get_customer_id(access_token)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "account_id": customer_id,
        }
    except Exception:
        logger.exception("Erro ao trocar código por token Google Ads")
        return None


def _get_customer_id(access_token):
    try:
        import requests

        developer_token = os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN")
        resp = requests.get(
            f"https://googleads.googleapis.com/{GOOGLE_ADS_API_VERSION}/customers:listAccessibleCustomers",
            headers={
                "Authorization": f"Bearer {access_token}",
                "developer-token": developer_token,
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        resource_names = data.get("resourceNames", [])
        if resource_names:
            return resource_names[0].split("/")[-1]
        return ""
    except Exception:
        logger.exception("Erro ao listar clientes Google Ads")
        return ""


def refresh_access_token(refresh_token):
    import requests

    client_id = os.environ.get("GOOGLE_ADS_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_ADS_CLIENT_SECRET")

    resp = requests.post(
        GOOGLE_TOKEN_URL,
        data={
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "refresh_token",
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def get_insights(access_token, customer_id, date_start, date_end):
    try:
        import requests

        developer_token = os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN")
        login_customer_id = os.environ.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID", customer_id)

        query = f"""
            SELECT
                campaign.id,
                campaign.name,
                ad_group.id,
                ad_group.name,
                ad_group_ad.ad.id,
                ad_group_ad.ad.name,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions
            FROM ad_group_ad
            WHERE segments.date BETWEEN '{date_start}' AND '{date_end}'
        """

        resp = requests.post(
            f"https://googleads.googleapis.com/{GOOGLE_ADS_API_VERSION}/customers/{customer_id}/googleAds:searchStream",
            headers={
                "Authorization": f"Bearer {access_token}",
                "developer-token": developer_token,
                "login-customer-id": login_customer_id,
                "Content-Type": "application/json",
            },
            json={"query": query},
            timeout=60,
        )
        resp.raise_for_status()

        results = []
        for batch in resp.json():
            for row in batch.get("results", []):
                campaign = row.get("campaign", {})
                ad_group = row.get("adGroup", {})
                ad = row.get("adGroupAd", {}).get("ad", {})
                metrics = row.get("metrics", {})

                cost_micros = int(metrics.get("costMicros", 0))
                results.append({
                    "campaign_id": str(campaign.get("id", "")),
                    "campaign_name": campaign.get("name", ""),
                    "adset_id": str(ad_group.get("id", "")),
                    "adset_name": ad_group.get("name", ""),
                    "ad_id": str(ad.get("id", "")),
                    "ad_name": ad.get("name", ""),
                    "impressions": int(metrics.get("impressions", 0)),
                    "clicks": int(metrics.get("clicks", 0)),
                    "spend": cost_micros / 1_000_000,
                    "leads": int(float(metrics.get("conversions", 0))),
                })
        return results
    except Exception:
        logger.exception("Erro ao buscar insights Google Ads para conta %s", customer_id)
        raise
