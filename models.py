# PROJECT: SecureWealth Twin | v3.3
import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, Numeric, DateTime, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from database import Base


def new_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id:               Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    name:             Mapped[str] = mapped_column(String(100), nullable=False)
    email:            Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    password_hash:    Mapped[str] = mapped_column(String(200), nullable=False)
    created_at:       Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    financial_profile: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    archetype:        Mapped[dict | None] = mapped_column(JSON, nullable=True)

    accounts: Mapped[list["Account"]] = relationship("Account", back_populates="user")
    goals:    Mapped[list["Goal"]]    = relationship("Goal", back_populates="user")


class Account(Base):
    __tablename__ = "accounts"

    id:             Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id:        Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    account_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    balance:        Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("100000.00"))
    created_at:     Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="accounts")
    sent_transactions:     Mapped[list["Transaction"]] = relationship("Transaction", foreign_keys="Transaction.sender_id",   back_populates="sender")
    received_transactions: Mapped[list["Transaction"]] = relationship("Transaction", foreign_keys="Transaction.receiver_id", back_populates="receiver")


class Transaction(Base):
    __tablename__ = "transactions"

    id:            Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    sender_id:     Mapped[str] = mapped_column(String(36), ForeignKey("accounts.id"), nullable=False)
    receiver_id:   Mapped[str | None] = mapped_column(String(36), ForeignKey("accounts.id"), nullable=True)
    amount:        Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    note:          Mapped[str] = mapped_column(String(200), default="")
    status:        Mapped[str] = mapped_column(String(20), default="completed")
    risk_score:    Mapped[int | None] = mapped_column(Integer, nullable=True)
    risk_decision: Mapped[str | None] = mapped_column(String(10), nullable=True)
    risk_signals:  Mapped[list | None] = mapped_column(JSON, nullable=True)
    timestamp:     Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    sender:   Mapped["Account"] = relationship("Account", foreign_keys=[sender_id],   back_populates="sent_transactions")
    receiver: Mapped["Account"] = relationship("Account", foreign_keys=[receiver_id], back_populates="received_transactions")


class Goal(Base):
    __tablename__ = "goals"

    id:             Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id:        Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    name:           Mapped[str] = mapped_column(String(100), nullable=False)
    target_amount:  Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    current_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0.00"))
    target_date:    Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at:     Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="goals")


class RiskAuditLog(Base):
    __tablename__ = "risk_audit_log"

    id:           Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    account_id:   Mapped[str | None] = mapped_column(String(36), nullable=True)
    action_type:  Mapped[str] = mapped_column(String(50), nullable=False)
    amount:       Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0"))
    risk_score:   Mapped[int] = mapped_column(Integer, default=0)
    level:        Mapped[str] = mapped_column(String(10), default="")
    decision:     Mapped[str] = mapped_column(String(10), default="")
    reason:       Mapped[str] = mapped_column(String(500), default="")
    signals:      Mapped[list | None] = mapped_column(JSON, nullable=True)
    trust_pyramid: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    timestamp:    Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
