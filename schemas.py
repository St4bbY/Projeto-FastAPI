from pydantic import BaseModel
from typing import Optional

class UsuarioSchema(BaseModel):
    nome: str
    email: str
    senha: str
    ativo: Optional[bool] = True 
    admin: Optional[bool] = False

    class Config:
        from_attributes = True

class LoginSchema(BaseModel):
    email: str
    senha: str

    class Config:
        from_attributes = True


class PedidoSchema(BaseModel):
    id_usuario: int
    status: Optional[str] = "PENDENTE"
    preco: Optional[float] = 0
    
    class Config:
        from_attributes = True