from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import create_access_token, verify_token
from app.config import settings
from app.database import get_db
from app.models import Client, Payment
from app.paypal_service import (
    cancel_subscription,
    create_product,
    create_subscription_plan,
    get_subscription_details,
)
from app.schemas import (
    ClientCreate,
    ClientResponse,
    ClientUpdate,
    DashboardStats,
    LoginRequest,
    PaymentResponse,
    TokenResponse,
)
from app.wave_service import create_invoice

router = APIRouter(prefix="/api")


# --- Auth ---


@router.post("/auth/login", response_model=TokenResponse)
async def login(req: LoginRequest):
    if req.username != settings.admin_username or req.password != settings.admin_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token({"sub": req.username})
    return TokenResponse(access_token=token)


# --- Dashboard ---


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard(db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    total_clients = (await db.execute(select(func.count(Client.id)))).scalar() or 0
    active_subs = (
        await db.execute(
            select(func.count(Client.id)).where(Client.subscription_status == "ACTIVE")
        )
    ).scalar() or 0
    monthly_rev = (
        await db.execute(
            select(func.sum(Client.monthly_amount)).where(
                Client.is_active.is_(True), Client.subscription_status == "ACTIVE"
            )
        )
    ).scalar() or 0.0
    total_collected = (
        await db.execute(
            select(func.sum(Payment.amount)).where(Payment.status == "completed")
        )
    ).scalar() or 0.0

    payments_result = await db.execute(
        select(Payment).order_by(Payment.created_at.desc()).limit(10)
    )
    recent_payments = []
    for p in payments_result.scalars().all():
        client = await db.get(Client, p.client_id)
        recent_payments.append(
            PaymentResponse(
                id=p.id,
                client_id=p.client_id,
                client_name=client.name if client else "",
                amount=p.amount,
                currency=p.currency,
                status=p.status,
                paypal_payment_id=p.paypal_payment_id,
                paid_at=p.paid_at.isoformat() if p.paid_at else None,
                created_at=p.created_at.isoformat(),
                wave_invoice_id=p.wave_invoice_id,
            )
        )

    return DashboardStats(
        total_clients=total_clients,
        active_subscriptions=active_subs,
        monthly_revenue=monthly_rev,
        total_collected=total_collected,
        recent_payments=recent_payments,
    )


# --- Clients ---


@router.get("/clients", response_model=list[ClientResponse])
async def list_clients(db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    result = await db.execute(select(Client).order_by(Client.created_at.desc()))
    clients = result.scalars().all()
    responses = []
    for c in clients:
        total_paid = (
            await db.execute(
                select(func.sum(Payment.amount)).where(
                    Payment.client_id == c.id, Payment.status == "completed"
                )
            )
        ).scalar() or 0.0
        payment_count = (
            await db.execute(
                select(func.count(Payment.id)).where(
                    Payment.client_id == c.id, Payment.status == "completed"
                )
            )
        ).scalar() or 0
        responses.append(
            ClientResponse(
                id=c.id,
                name=c.name,
                email=c.email,
                company=c.company,
                monthly_amount=c.monthly_amount,
                currency=c.currency,
                description=c.description,
                is_active=c.is_active,
                subscription_status=c.subscription_status,
                payment_token=c.payment_token,
                paypal_plan_id=c.paypal_plan_id,
                paypal_subscription_id=c.paypal_subscription_id,
                created_at=c.created_at.isoformat(),
                total_paid=total_paid,
                payment_count=payment_count,
            )
        )
    return responses


@router.post("/clients", response_model=ClientResponse, status_code=201)
async def create_client(
    data: ClientCreate, db: AsyncSession = Depends(get_db), _=Depends(verify_token)
):
    existing = (
        await db.execute(select(Client).where(Client.email == data.email))
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Client with this email already exists")

    client = Client(
        name=data.name,
        email=data.email,
        company=data.company,
        monthly_amount=data.monthly_amount,
        currency=data.currency,
        description=data.description,
    )

    # Create PayPal product and plan if credentials are configured
    if settings.paypal_client_id and settings.paypal_client_secret:
        try:
            product_id = await create_product(
                f"Web Services - {data.name}",
                data.description or "Monthly web services",
            )
            plan_id = await create_subscription_plan(
                product_id,
                f"Monthly Plan - {data.name}",
                data.monthly_amount,
                data.currency,
            )
            client.paypal_plan_id = plan_id
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to create PayPal plan: {e}"
            )

    db.add(client)
    await db.commit()
    await db.refresh(client)

    return ClientResponse(
        id=client.id,
        name=client.name,
        email=client.email,
        company=client.company,
        monthly_amount=client.monthly_amount,
        currency=client.currency,
        description=client.description,
        is_active=client.is_active,
        subscription_status=client.subscription_status,
        payment_token=client.payment_token,
        paypal_plan_id=client.paypal_plan_id,
        paypal_subscription_id=client.paypal_subscription_id,
        created_at=client.created_at.isoformat(),
    )


@router.put("/clients/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: str,
    data: ClientUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_token),
):
    client = await db.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(client, field, value)

    await db.commit()
    await db.refresh(client)

    return ClientResponse(
        id=client.id,
        name=client.name,
        email=client.email,
        company=client.company,
        monthly_amount=client.monthly_amount,
        currency=client.currency,
        description=client.description,
        is_active=client.is_active,
        subscription_status=client.subscription_status,
        payment_token=client.payment_token,
        paypal_plan_id=client.paypal_plan_id,
        paypal_subscription_id=client.paypal_subscription_id,
        created_at=client.created_at.isoformat(),
    )


@router.delete("/clients/{client_id}")
async def delete_client(
    client_id: str, db: AsyncSession = Depends(get_db), _=Depends(verify_token)
):
    client = await db.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    if client.paypal_subscription_id and client.subscription_status == "ACTIVE":
        try:
            await cancel_subscription(client.paypal_subscription_id)
        except Exception:
            pass

    await db.delete(client)
    await db.commit()
    return {"detail": "Client deleted"}


@router.post("/clients/{client_id}/sync-subscription")
async def sync_subscription(
    client_id: str, db: AsyncSession = Depends(get_db), _=Depends(verify_token)
):
    client = await db.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    if not client.paypal_subscription_id:
        raise HTTPException(status_code=400, detail="No subscription to sync")

    details = await get_subscription_details(client.paypal_subscription_id)
    client.subscription_status = details.get("status", client.subscription_status)
    await db.commit()
    return {"status": client.subscription_status}


# --- Payments ---


@router.get("/payments", response_model=list[PaymentResponse])
async def list_payments(db: AsyncSession = Depends(get_db), _=Depends(verify_token)):
    result = await db.execute(select(Payment).order_by(Payment.created_at.desc()).limit(100))
    payments = []
    for p in result.scalars().all():
        client = await db.get(Client, p.client_id)
        payments.append(
            PaymentResponse(
                id=p.id,
                client_id=p.client_id,
                client_name=client.name if client else "",
                amount=p.amount,
                currency=p.currency,
                status=p.status,
                paypal_payment_id=p.paypal_payment_id,
                paid_at=p.paid_at.isoformat() if p.paid_at else None,
                created_at=p.created_at.isoformat(),
                wave_invoice_id=p.wave_invoice_id,
            )
        )
    return payments


@router.post("/payments/{payment_id}/sync-wave")
async def sync_payment_to_wave(
    payment_id: str, db: AsyncSession = Depends(get_db), _=Depends(verify_token)
):
    payment = await db.get(Payment, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    client = await db.get(Client, payment.client_id)
    result = await create_invoice(
        client_name=client.name,
        client_email=client.email,
        amount=payment.amount,
        currency=payment.currency,
        description=client.description or "Monthly web services",
    )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    invoice_data = result.get("data", {}).get("invoiceCreate", {}).get("invoice", {})
    if invoice_data:
        payment.wave_invoice_id = invoice_data.get("id")
        await db.commit()

    return result
