import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use a clean test database file
TEST_DB_URL = "sqlite:///./test_steam_intel.db"
os.environ["DATABASE_URL"] = TEST_DB_URL
os.environ["APP_ENV"] = "test"

from app.core.database import Base, get_db
from app.main import app

test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()
    try:
        if os.path.exists("./test_steam_intel.db"):
            os.remove("./test_steam_intel.db")
    except Exception:
        pass


@pytest.fixture(autouse=True)
def clean_tables_after_test():
    yield
    with test_engine.connect() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
        conn.commit()


@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client, db_session):
    from app.core.security import create_access_token
    from app.models.user import User, Role, UserRole
    import uuid

    # Ensure role exists
    owner_role = db_session.query(Role).filter(Role.name == "owner").first()
    if not owner_role:
        owner_role = Role(id=uuid.uuid4(), name="owner", description="Owner role")
        db_session.add(owner_role)
        db_session.commit()

    test_user = db_session.query(User).filter(User.email == "test_authed@steamintel.internal").first()
    if not test_user:
        test_user = User(
            id=uuid.uuid4(),
            email="test_authed@steamintel.internal",
            password_hash="hashed_placeholder",
            display_name="Test Authed User",
            is_active=True
        )
        db_session.add(test_user)
        db_session.commit()

        ur = UserRole(user_id=test_user.id, role_id=owner_role.id)
        db_session.add(ur)
        db_session.commit()

    token = create_access_token(subject=str(test_user.id), roles=["owner"])
    return {"Authorization": f"Bearer {token}"}
