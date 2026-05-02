# PROJECT: SecureWealth Twin | v3.0-production
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import JSON
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100))
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    financial_profile = Column(JSON, nullable=True)
    archetype = Column(JSON, nullable=True)
    
    accounts = relationship("Account", back_populates="user")
    goals = relationship("Goal", back_populates="user")

class Account(Base):
    __tablename__ = "accounts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    account_number = Column(String(20), unique=True)
    balance = Column(Numeric(15, 2), default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="accounts")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"))
    receiver_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True)
    amount = Column(Numeric(15, 2))
    note = Column(String(200), default='')
    status = Column(String(20), default='completed')
    risk_score = Column(Integer, nullable=True)
    risk_decision = Column(String(10), nullable=True)
    risk_signals = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class Goal(Base):
    __tablename__ = "goals"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    name = Column(String(100))
    target_amount = Column(Numeric(15, 2))
    current_amount = Column(Numeric(15, 2), default=0)
    target_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="goals")

class RiskAuditLog(Base):
    __tablename__ = "risk_audit_log"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True)
    action_type = Column(String(50))
    amount = Column(Numeric(15, 2))
    risk_score = Column(Integer)
    level = Column(String(10))
    decision = Column(String(10))
    reason = Column(String(500))
    signals = Column(JSON)
    trust_pyramid = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)
