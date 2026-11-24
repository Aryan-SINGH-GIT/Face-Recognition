import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from app.db.database import Base

class RegisteredUser(Base):
    """End-user registered via face enrollment (self-service portal)."""
    __tablename__ = "registered_users"

    id          = Column(Integer, primary_key=True, index=True)
    full_name   = Column(String(100), unique=True, index=True, nullable=False)
    display_name = Column(String(100), nullable=True)   # optional friendly name
    is_active   = Column(Boolean, default=True)
    registered_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_seen_at  = Column(DateTime, nullable=True)
    total_access  = Column(Integer, default=0)

class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    role = Column(String(20), default="ADMIN")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class AccessLog(Base):
    __tablename__ = "access_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    status = Column(String(30), nullable=False) # GRANTED, DENIED, SPOOF_DETECTED, NO_FACE
    matched_identity = Column(String(100), nullable=True)
    l2_distance = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)
    is_live = Column(Boolean, default=True)
    liveness_score = Column(Float, nullable=True)
    ip_address = Column(String(50), nullable=True)
    message = Column(String(255), nullable=True)

class RevokedToken(Base):
    """Server-side blacklist for logged-out JWT tokens."""
    __tablename__ = "revoked_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(512), unique=True, index=True, nullable=False)
    revoked_at = Column(DateTime, default=datetime.datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)

class SystemSetting(Base):
    """System-level dynamic configuration settings managed by Admins."""
    __tablename__ = "system_settings"

    key = Column(String(50), primary_key=True, index=True)
    value = Column(String(255), nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


