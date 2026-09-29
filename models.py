import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    create_engine,
    text,
)
from sqlalchemy.orm import declarative_base, relationship

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///banco.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
db = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)

Base = declarative_base()


class Usuario(Base):
    __tablename__ = "usuarios"
    __table_args__ = (Index("uq_usuarios_email_ci", text("lower(email)"), unique=True),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    senha = Column(String(255), nullable=False)
    ativo = Column(Boolean, nullable=False, default=True)
    admin = Column(Boolean, nullable=False, default=False)
    pedidos = relationship("Pedido", back_populates="cliente")

    def __init__(self, nome, email, senha, ativo=True, admin=False):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.ativo = ativo
        self.admin = admin


class Produto(Base):
    __tablename__ = "produtos"
    __table_args__ = (UniqueConstraint("sabor", "tamanho", name="uq_produto_sabor_tamanho"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    sabor = Column(String(80), nullable=False)
    tamanho = Column(String(1), nullable=False)
    preco = Column(Float, nullable=False)
    ativo = Column(Boolean, nullable=False, default=True)


class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(String(20), nullable=False, default="PENDENTE")
    usuario = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    preco = Column(Float, nullable=False, default=0)
    criado_em = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    cliente = relationship("Usuario", back_populates="pedidos")
    itens = relationship("ItemPedido", back_populates="ordem", cascade="all, delete-orphan")

    def __init__(self, usuario, status="PENDENTE", preco=0):
        self.usuario = usuario
        self.status = status
        self.preco = preco


class ItemPedido(Base):
    __tablename__ = "itens_pedido"

    id = Column(Integer, primary_key=True, autoincrement=True)
    quantidade = Column(Integer, nullable=False)
    sabor = Column(String(80), nullable=False)
    tamanho = Column(String(1), nullable=False)
    preco_unitario = Column(Float, nullable=False)
    pedido_id = Column("pedido", Integer, ForeignKey("pedidos.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=True)
    ordem = relationship("Pedido", back_populates="itens")
    produto = relationship("Produto")

    def __init__(self, quantidade, sabor, tamanho, preco_unitario, pedido=None, produto_id=None):
        self.quantidade = quantidade
        self.sabor = sabor
        self.tamanho = tamanho
        self.preco_unitario = preco_unitario
        if pedido is not None:
            self.ordem = pedido if isinstance(pedido, Pedido) else None
            if not isinstance(pedido, Pedido):
                self.pedido_id = pedido
        self.produto_id = produto_id
