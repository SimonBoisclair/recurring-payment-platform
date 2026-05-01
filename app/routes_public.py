import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import Client, Payment

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/pay/{token}", response_class=HTMLResponse)
async def payment_page(request: Request, token: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Client).where(Client.payment_token == token))
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Payment link not found")
    if not client.is_active:
        raise HTTPException(status_code=400, detail="This payment link is no longer active")

    return templates.TemplateResponse(
        request,
        "payment.html",
        {
            "client": client,
            "paypal_client_id": settings.paypal_client_id,
            "paypal_plan_id": client.paypal_plan_id,
        },
    )


@router.get("/pay/{token}/success", response_class=HTMLResponse)
async def payment_success(
    request: Request, token: str, subscription_id: str = "", db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Client).where(Client.payment_token == token))
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Payment link not found")

    if subscription_id:
        client.paypal_subscription_id = subscription_id
        client.subscription_status = "ACTIVE"

        payment = Payment(
            client_id=client.id,
            amount=client.monthly_amount,
            currency=client.currency,
            status="completed",
            paypal_payment_id=subscription_id,
            paid_at=datetime.datetime.utcnow(),
        )
        db.add(payment)
        await db.commit()

    return templates.TemplateResponse(
        request,
        "payment_success.html",
        {"client": client},
    )


@router.post("/webhooks/paypal")
async def paypal_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    body = await request.json()
    event_type = body.get("event_type", "")

    if event_type == "PAYMENT.SALE.COMPLETED":
        resource = body.get("resource", {})
        subscription_id = resource.get("billing_agreement_id")
        amount = float(resource.get("amount", {}).get("total", 0))
        currency = resource.get("amount", {}).get("currency", "CAD")

        if subscription_id:
            result = await db.execute(
                select(Client).where(Client.paypal_subscription_id == subscription_id)
            )
            client = result.scalar_one_or_none()
            if client:
                payment = Payment(
                    client_id=client.id,
                    amount=amount,
                    currency=currency,
                    status="completed",
                    paypal_payment_id=resource.get("id"),
                    paid_at=datetime.datetime.utcnow(),
                )
                db.add(payment)
                await db.commit()

    elif event_type == "BILLING.SUBSCRIPTION.CANCELLED":
        resource = body.get("resource", {})
        subscription_id = resource.get("id")
        if subscription_id:
            result = await db.execute(
                select(Client).where(Client.paypal_subscription_id == subscription_id)
            )
            client = result.scalar_one_or_none()
            if client:
                client.subscription_status = "CANCELLED"
                await db.commit()

    return {"status": "ok"}
