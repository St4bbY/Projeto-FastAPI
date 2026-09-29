from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from dependencies import pegar_sessao
from schemas import PedidoSchema
from models import Pedido
from models import Usuario
from auth_dependencies import usuario_atual

order_router = APIRouter(prefix="/pedidos", tags=["pedidos"])

@order_router.get("/")
async def pedidos():
    """
    Essa é a rota de pedidos!
    """
    return {"mensagem":"Você está na rota de pedidos!"}

@order_router.post("/pedido")
async def criar_pedido(
    pedido_schema: PedidoSchema,
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(usuario_atual),
):
    novo_pedido = Pedido(
        usuario=usuario.id,
        status=pedido_schema.status,
        preco=pedido_schema.preco,
    )
    session.add(novo_pedido)
    session.commit()
    session.refresh(novo_pedido)

    return {
        "mensagem": f"Pedido criado com sucesso! ID do pedido: {novo_pedido.id}"
    }
