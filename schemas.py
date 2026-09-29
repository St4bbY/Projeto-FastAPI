from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


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


class PedidoCriar(BaseModel):
    preco: float = Field(default=0, ge=0, le=1_000_000)


class PedidoResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario: int
    status: Literal["PENDENTE", "CANCELADO", "FINALIZADO"]
    preco: float
