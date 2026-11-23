from datetime import datetime, timezone
from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import (
    verify_password, get_password_hash, create_access_token, decode_access_token
)
from app.models.user import User, Role, UserRole, AuditLog
from app.schemas.auth import Token, UserLogin, UserCreate, UserResponse

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_uuid, User.is_active == True).first()
    if user is None:
        raise credentials_exception
    return user


def require_roles(allowed_roles: List[str]):
    def role_checker(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        user_roles = [ur.role.name for ur in current_user.user_roles]
        if not any(r in allowed_roles for r in user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions for this operation"
            )
        return current_user
    return role_checker


@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user account")

    roles = [ur.role.name for ur in user.user_roles]
    token = create_access_token(subject=str(user.id), roles=roles)

    # Update last login
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()

    return Token(
        access_token=token,
        token_type="bearer",
        expires_in=60 * 24 * 60,
        roles=roles,
        user_id=str(user.id),
        email=user.email
    )


@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """OAuth2 password form compatible endpoint for OpenAPI docs."""
    return login(UserLogin(email=form_data.username, password=form_data.password), db=db)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    # Check if user with this email already exists
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    # Check total user count: if 0, bootstrap first user as 'owner'
    user_count = db.query(User).count()
    assigned_role_name = "owner" if user_count == 0 else user_in.role

    # Ensure role exists in DB
    role = db.query(Role).filter(Role.name == assigned_role_name).first()
    if not role:
        role = Role(
            id=uuid.uuid4(),
            name=assigned_role_name,
            description=f"System {assigned_role_name} role"
        )
        db.add(role)
        db.flush()

    new_user = User(
        id=uuid.uuid4(),
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        display_name=user_in.display_name or user_in.email.split("@")[0],
        is_active=True,
        created_at=datetime.now(timezone.utc)
    )
    db.add(new_user)
    db.flush()

    user_role = UserRole(user_id=new_user.id, role_id=role.id)
    db.add(user_role)

    # Audit log
    audit = AuditLog(
        id=uuid.uuid4(),
        actor_id=new_user.id,
        action="USER_REGISTERED",
        resource_type="user",
        resource_id=str(new_user.id),
        metadata_json={"role": assigned_role_name}
    )
    db.add(audit)
    db.commit()
    db.refresh(new_user)

    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        display_name=new_user.display_name,
        is_active=new_user.is_active,
        roles=[assigned_role_name],
        created_at=new_user.created_at,
        last_login_at=new_user.last_login_at
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    roles = [ur.role.name for ur in current_user.user_roles]
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        display_name=current_user.display_name,
        is_active=current_user.is_active,
        roles=roles,
        created_at=current_user.created_at,
        last_login_at=current_user.last_login_at
    )
