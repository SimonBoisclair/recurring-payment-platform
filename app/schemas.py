from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ClientCreate(BaseModel):
    name: str
    email: EmailStr
    company: str | None = None
    monthly_amount: float
    currency: str = "CAD"
    description: str | None = None


class ClientUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    company: str | None = None
    monthly_amount: float | None = None
    currency: str | None = None
    description: str | None = None
    is_active: bool | None = None


class ClientResponse(BaseModel):
    id: str
    name: str
    email: str
    company: str | None
    monthly_amount: float
    currency: str
    description: str | None
    is_active: bool
    subscription_status: str
    payment_token: str
    paypal_plan_id: str | None
    paypal_subscription_id: str | None
    created_at: str
    total_paid: float = 0.0
    payment_count: int = 0

    model_config = {"from_attributes": True}


class PaymentResponse(BaseModel):
    id: str
    client_id: str
    client_name: str = ""
    amount: float
    currency: str
    status: str
    paypal_payment_id: str | None
    paid_at: str | None
    created_at: str
    wave_invoice_id: str | None

    model_config = {"from_attributes": True}


class DashboardStats(BaseModel):
    total_clients: int
    active_subscriptions: int
    monthly_revenue: float
    total_collected: float
    recent_payments: list[PaymentResponse]
