import os

os.environ.setdefault("SECRET_KEY", "test-only-secret-key-not-for-production")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from dependencies import pegar_sessao
from main import app
from models import Base, Produto


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def override_session():
        session = TestingSession()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[pegar_sessao] = override_session
    with TestingSession() as session:
        session.add_all(
            [
                Produto(sabor="Calabresa", tamanho="P", preco=32.90, ativo=True),
                Produto(sabor="Margherita", tamanho="M", preco=39.90, ativo=True),
            ]
        )
        session.commit()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


