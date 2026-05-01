import httpx

from app.config import settings

WAVE_GRAPHQL_URL = "https://gql.waveapps.com/graphql/public"


async def _wave_request(query: str, variables: dict | None = None) -> dict:
    if not settings.wave_api_token:
        return {"error": "Wave API token not configured"}
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            WAVE_GRAPHQL_URL,
            headers={
                "Authorization": f"Bearer {settings.wave_api_token}",
                "Content-Type": "application/json",
            },
            json={"query": query, "variables": variables or {}},
        )
        resp.raise_for_status()
        return resp.json()


async def list_businesses() -> dict:
    query = """
    query {
        businesses(page: 1, pageSize: 10) {
            edges {
                node {
                    id
                    name
                }
            }
        }
    }
    """
    return await _wave_request(query)


async def create_invoice(
    client_name: str,
    client_email: str,
    amount: float,
    currency: str = "CAD",
    description: str = "Monthly web services",
) -> dict:
    if not settings.wave_business_id:
        return {"error": "Wave business ID not configured"}

    query = """
    mutation CreateInvoice($input: InvoiceCreateInput!) {
        invoiceCreate(input: $input) {
            invoice {
                id
                invoiceNumber
                status
                total { value currency { code } }
            }
            didSucceed
            inputErrors { path message code }
        }
    }
    """
    variables = {
        "input": {
            "businessId": settings.wave_business_id,
            "customerId": None,
            "status": "SAVED",
            "currency": currency,
            "items": [
                {
                    "description": description,
                    "unitPrice": str(amount),
                    "quantity": 1,
                }
            ],
        }
    }
    return await _wave_request(query, variables)


async def get_invoices() -> dict:
    if not settings.wave_business_id:
        return {"error": "Wave business ID not configured"}

    query = """
    query GetInvoices($businessId: ID!) {
        business(id: $businessId) {
            invoices(page: 1, pageSize: 50) {
                edges {
                    node {
                        id
                        invoiceNumber
                        status
                        total { value currency { code } }
                        customer { name email }
                        createdAt
                    }
                }
            }
        }
    }
    """
    return await _wave_request(query, {"businessId": settings.wave_business_id})
