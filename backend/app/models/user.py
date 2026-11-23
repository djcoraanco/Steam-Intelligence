import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Text, Boolean, DateTime,
    ForeignKey, PrimaryKeyConstraint
)
from sqlalchemy.orm import relationship
from app.core.database import Base, GUID, UniversalJSON


def now_utc():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    display_name = Column(String(120), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=now_utc)
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    user_roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")


class Role(Base):
    __tablename__ = "roles"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(40), unique=True, nullable=False)  # owner, admin, analyst, viewer
    description = Column(Text, nullable=True)

    role_users = relationship("UserRole", back_populates="role")


class UserRole(Base):
    __tablename__ = "user_roles"
    __table_args__ = (
        PrimaryKeyConstraint("user_id", "role_id", name="pk_user_roles"),
    )

    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role_id = Column(GUID, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)

    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="role_users")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    actor_id = Column(GUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(60), nullable=False)
    resource_id = Column(String(120), nullable=True)
    timestamp = Column(DateTime(timezone=True), default=now_utc, index=True)
    ip_address = Column(String(45), nullable=True)
    metadata_json = Column(UniversalJSON, default=dict)
