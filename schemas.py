from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


class UsuarioCriar(BaseModel):
    nome: str = Field(min_length=2, max_length=100)
    email: EmailStr
    senha: str = Field(min_length=8, max_length=72)

    @field_validator("senha")
    @classmethod
    def validar_tamanho_senha(cls, senha: str) -> str:
        if len(senha.encode("utf-8")) > 72:
            raise ValueError("A senha deve ter no máximo 72 bytes")
        return senha


class LoginSchema(BaseModel):
    email: EmailStr
    senha: str = Field(max_length=72)

    @field_validator("senha")
    @classmethod
    def validar_tamanho_senha(cls, senha: str) -> str:
        if len(senha.encode("utf-8")) > 72:
            raise ValueError("A senha deve ter no máximo 72 bytes")
        return senha


class UsuarioPublico(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    email: EmailStr


class TokenResposta(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PedidoItemCriar(BaseModel):
    produto_id: int = Field(gt=0)
    quantidade: int = Field(ge=1, le=20)


class PedidoCriar(BaseModel):
    itens: list[PedidoItemCriar] = Field(min_length=1, max_length=20)

    @model_validator(mode="after")
    def limitar_quantidade_por_produto(self):
        quantidades: dict[int, int] = {}
        for item in self.itens:
            quantidades[item.produto_id] = quantidades.get(item.produto_id, 0) + item.quantidade
        if any(quantidade > 20 for quantidade in quantidades.values()):
            raise ValueError("A quantidade máxima por produto é 20")
        return self


class ProdutoResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sabor: str
    tamanho: Literal["P", "M", "G"]
    preco: float


class PedidoItemResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    produto_id: int | None
    sabor: str
    tamanho: str
    quantidade: int
    preco_unitario: float


class PedidoResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario: int
    status: Literal["PENDENTE", "CANCELADO", "FINALIZADO"]
    preco: float
    criado_em: datetime
    itens: list[PedidoItemResposta]


class PaginaPedidos(BaseModel):
    itens: list[PedidoResposta]
    total: int
    limite: int
    deslocamento: int
