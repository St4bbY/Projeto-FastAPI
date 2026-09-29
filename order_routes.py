from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, selectinload

from auth_dependencies import usuario_atual
from dependencies import pegar_sessao
from models import ItemPedido, Pedido, Produto, Usuario
from schemas import (
    PaginaPedidos,
    PedidoCriar,
    PedidoResposta,
    ProdutoResposta,
)

order_router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


@order_router.get("/catalogo", response_model=list[ProdutoResposta], summary="Ver catálogo")
def listar_catalogo(session: Session = Depends(pegar_sessao)):
    return (
        session.query(Produto)
        .filter(Produto.ativo.is_(True))
        .order_by(Produto.sabor, Produto.tamanho)
        .all()
    )


@order_router.get("/", response_model=PaginaPedidos, summary="Listar meus pedidos")
def listar_pedidos(
    deslocamento: int = Query(default=0, ge=0),
    limite: int = Query(default=20, ge=1, le=100),
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(usuario_atual),
):
    consulta = session.query(Pedido).filter(Pedido.usuario == usuario.id)
    total = consulta.count()
    itens = (
        consulta.options(selectinload(Pedido.itens))
        .order_by(Pedido.criado_em.desc(), Pedido.id.desc())
        .offset(deslocamento)
        .limit(limite)
        .all()
    )
    return PaginaPedidos(
        itens=itens,
        total=total,
        limite=limite,
        deslocamento=deslocamento,
    )


@order_router.post(
    "/",
    response_model=PedidoResposta,
    status_code=status.HTTP_201_CREATED,
    summary="Criar pedido a partir do catálogo",
)
def criar_pedido(
    dados: PedidoCriar,
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(usuario_atual),
):
    produtos_ids = {item.produto_id for item in dados.itens}
    produtos = (
        session.query(Produto)
        .filter(Produto.id.in_(produtos_ids), Produto.ativo.is_(True))
        .all()
    )
    produtos_por_id = {produto.id: produto for produto in produtos}
    ids_invalidos = sorted(produtos_ids - produtos_por_id.keys())
    if ids_invalidos:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Produto(s) inexistente(s) ou indisponível(is): {ids_invalidos}",
        )

    quantidades_por_produto: dict[int, int] = {}
    for item in dados.itens:
        quantidades_por_produto[item.produto_id] = (
            quantidades_por_produto.get(item.produto_id, 0) + item.quantidade
        )

    linhas = []
    total = Decimal("0.00")
    for produto_id, quantidade in quantidades_por_produto.items():
        produto = produtos_por_id[produto_id]
        total += Decimal(str(produto.preco)) * quantidade
        linhas.append(
            ItemPedido(
                quantidade=quantidade,
                sabor=produto.sabor,
                tamanho=produto.tamanho,
                preco_unitario=produto.preco,
                produto_id=produto.id,
            )
        )

    pedido = Pedido(usuario=usuario.id, status="PENDENTE", preco=float(total))
    pedido.itens = linhas
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
        .options(selectinload(Pedido.itens))
        .filter(Pedido.id == pedido_id, Pedido.usuario == usuario.id)
        .first()
    )
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return pedido


@order_router.patch(
    "/{pedido_id}/cancelar",
    response_model=PedidoResposta,
    summary="Cancelar pedido pendente",
)
def cancelar_pedido(
    pedido_id: int,
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(usuario_atual),
):
    pedido = (
        session.query(Pedido)
        .options(selectinload(Pedido.itens))
        .filter(Pedido.id == pedido_id, Pedido.usuario == usuario.id)
        .first()
    )
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    if pedido.status != "PENDENTE":
        raise HTTPException(
            status_code=409,
            detail="Somente pedidos pendentes podem ser cancelados",
        )

    pedido.status = "CANCELADO"
    session.commit()
    session.refresh(pedido)
    return pedido
