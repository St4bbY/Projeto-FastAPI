from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth_dependencies import usuario_atual
from dependencies import pegar_sessao
from models import Pedido, Usuario
from schemas import PedidoCriar, PedidoResposta

order_router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


@order_router.get("/", response_model=list[PedidoResposta], summary="Listar meus pedidos")
def listar_pedidos(
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(usuario_atual),
):
    return (
        session.query(Pedido)
        .filter(Pedido.usuario == usuario.id)
        .order_by(Pedido.id.desc())
        .all()
    )


@order_router.post(
    "/",
    response_model=PedidoResposta,
    status_code=status.HTTP_201_CREATED,
    summary="Criar pedido",
)
@order_router.post("/pedido", response_model=PedidoResposta, status_code=status.HTTP_201_CREATED, include_in_schema=False)
def criar_pedido(
    dados: PedidoCriar,
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(usuario_atual),
):
    pedido = Pedido(usuario=usuario.id, status="PENDENTE", preco=dados.preco)
    session.add(pedido)
    session.commit()
    session.refresh(pedido)
    return pedido


@order_router.get("/{pedido_id}", response_model=PedidoResposta, summary="Consultar pedido")
def obter_pedido(
    pedido_id: int,
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(usuario_atual),
):
    pedido = (
        session.query(Pedido)
        .filter(Pedido.id == pedido_id, Pedido.usuario == usuario.id)
        .first()
    )
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return pedido


@order_router.patch("/{pedido_id}/cancelar", response_model=PedidoResposta, summary="Cancelar pedido")
def cancelar_pedido(
    pedido_id: int,
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(usuario_atual),
):
    pedido = (
        session.query(Pedido)
        .filter(Pedido.id == pedido_id, Pedido.usuario == usuario.id)
        .first()
    )
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    if pedido.status != "PENDENTE":
        raise HTTPException(status_code=409, detail="Somente pedidos pendentes podem ser cancelados")

    pedido.status = "CANCELADO"
    session.commit()
    session.refresh(pedido)
    return pedido
