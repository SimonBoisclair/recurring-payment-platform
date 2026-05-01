import datetime
import uuid

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    company: Mapped[str | None] = mapped_column(String(200), nullable=True)
    monthly_amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="CAD")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )

    # PayPal
    paypal_plan_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    paypal_subscription_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    subscription_status: Mapped[str] = mapped_column(String(50), default="pending")

    # Payment link token
    payment_token: Mapped[str] = mapped_column(
        String(64), unique=True, default=lambda: uuid.uuid4().hex
    )

    payments: Mapped[list["Payment"]] = relationship(back_populates="client", lazy="selectin")


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    client_id: Mapped[str] = mapped_column(String(36), ForeignKey("clients.id"), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="CAD")
    status: Mapped[str] = mapped_column(String(50), default="pending")
    paypal_payment_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    paid_at: Mapped[datetime.datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )

    # Wave sync
    wave_invoice_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    client: Mapped["Client"] = relationship(back_populates="payments")
