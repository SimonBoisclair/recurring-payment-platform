import base64

import httpx

from app.config import settings


async def _get_access_token() -> str:
    credentials = base64.b64encode(
        f"{settings.paypal_client_id}:{settings.paypal_client_secret}".encode()
    ).decode()
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{settings.paypal_base_url}/v1/oauth2/token",
            headers={
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={"grant_type": "client_credentials"},
        )
        resp.raise_for_status()
        return resp.json()["access_token"]


async def create_product(name: str, description: str) -> str:
    token = await _get_access_token()
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{settings.paypal_base_url}/v1/catalogs/products",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json={
                "name": name,
                "description": description or "Monthly web service",
                "type": "SERVICE",
                "category": "SOFTWARE",
            },
        )
        resp.raise_for_status()
        return resp.json()["id"]


async def create_subscription_plan(
    product_id: str, plan_name: str, amount: float, currency: str = "CAD"
) -> str:
    token = await _get_access_token()
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{settings.paypal_base_url}/v1/billing/plans",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json={
                "product_id": product_id,
                "name": plan_name,
                "billing_cycles": [
                    {
                        "frequency": {"interval_unit": "MONTH", "interval_count": 1},
                        "tenure_type": "REGULAR",
                        "sequence": 1,
                        "total_cycles": 0,
                        "pricing_scheme": {
                            "fixed_price": {
                                "value": str(amount),
                                "currency_code": currency,
                            }
                        },
                    }
                ],
                "payment_preferences": {
                    "auto_bill_outstanding": True,
                    "payment_failure_threshold": 3,
                },
            },
        )
        resp.raise_for_status()
        return resp.json()["id"]


async def get_subscription_details(subscription_id: str) -> dict:
    token = await _get_access_token()
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{settings.paypal_base_url}/v1/billing/subscriptions/{subscription_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        resp.raise_for_status()
        return resp.json()


async def cancel_subscription(subscription_id: str, reason: str = "Cancelled by admin") -> None:
    token = await _get_access_token()
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{settings.paypal_base_url}/v1/billing/subscriptions/{subscription_id}/cancel",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json={"reason": reason},
        )
        resp.raise_for_status()
