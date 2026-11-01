import logging
import os

logger = logging.getLogger(__name__)


def get_oauth_url(redirect_uri, state=None):
    app_id = os.environ.get("META_APP_ID")
    params = (
        f"https://www.facebook.com/v19.0/dialog/oauth"
        f"?client_id={app_id}"
        f"&redirect_uri={redirect_uri}"
        f"&scope=ads_read"
        f"&response_type=code"
    )
    if state:
        params += f"&state={state}"
    return params


def exchange_code_for_token(code, redirect_uri):
    try:
        import requests
        from facebook_business.api import FacebookAdsApi

        app_id = os.environ.get("META_APP_ID")
        app_secret = os.environ.get("META_APP_SECRET")

        resp = requests.get(
            "https://graph.facebook.com/v19.0/oauth/access_token",
            params={
                "client_id": app_id,
                "client_secret": app_secret,
                "redirect_uri": redirect_uri,
                "code": code,
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        access_token = data["access_token"]

        FacebookAdsApi.init(
            app_id=app_id, app_secret=app_secret, access_token=access_token
        )
        from facebook_business.adobjects.user import User

        me = User(fbid="me")
        accounts = me.get_ad_accounts(fields=["account_id", "name"])
        account_id = accounts[0]["account_id"] if accounts else ""

        return {"access_token": access_token, "account_id": account_id}
    except Exception:
        logger.exception("Erro ao trocar código por token Meta")
        return None


def get_insights(access_token, account_id, date_start, date_end):
    try:
        from facebook_business.adobjects.adaccount import AdAccount
        from facebook_business.api import FacebookAdsApi

        app_id = os.environ.get("META_APP_ID")
        app_secret = os.environ.get("META_APP_SECRET")
        FacebookAdsApi.init(
            app_id=app_id, app_secret=app_secret, access_token=access_token
        )

        account = AdAccount(f"act_{account_id}")
        params = {
            "time_range": {"since": date_start, "until": date_end},
            "level": "ad",
            "fields": [
                "campaign_id",
                "campaign_name",
                "adset_id",
                "adset_name",
                "ad_id",
                "ad_name",
                "impressions",
                "clicks",
                "spend",
                "actions",
            ],
        }
        insights = account.get_insights(params=params)

        results = []
        for row in insights:
            leads_count = 0
            if "actions" in row:
                for action in row["actions"]:
                    if action.get("action_type") == "lead":
                        leads_count = int(action.get("value", 0))
                        break

            results.append(
                {
                    "campaign_id": row.get("campaign_id", ""),
                    "campaign_name": row.get("campaign_name", ""),
                    "adset_id": row.get("adset_id", ""),
                    "adset_name": row.get("adset_name", ""),
                    "ad_id": row.get("ad_id", ""),
                    "ad_name": row.get("ad_name", ""),
                    "impressions": int(row.get("impressions", 0)),
                    "clicks": int(row.get("clicks", 0)),
                    "spend": float(row.get("spend", 0)),
                    "leads": leads_count,
                }
            )
        return results
    except Exception:
        logger.exception("Erro ao buscar insights Meta para conta %s", account_id)
        raise
