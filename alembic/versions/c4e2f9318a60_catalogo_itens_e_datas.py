"""Adiciona catálogo, itens, data do pedido e email único sem distinção de caixa.

Revision ID: c4e2f9318a60
Revises: f7d3f50d8af8
Create Date: 2026-09-29
"""
from alembic import op
import sqlalchemy as sa


revision = "c4e2f9318a60"
down_revision = "f7d3f50d8af8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    duplicates = bind.execute(
        sa.text(
            "SELECT lower(trim(email)), count(*) FROM usuarios "
            "GROUP BY lower(trim(email)) HAVING count(*) > 1"
        )
    ).fetchall()
    if duplicates:
        raise RuntimeError(
            "Não foi possível criar índice único: há e-mails duplicados em usuarios. "
            "Corrija os registros duplicados e execute alembic upgrade head novamente."
        )

    op.execute(sa.text("UPDATE usuarios SET email = lower(trim(email))"))
    if not any(
        index["name"] == "uq_usuarios_email_ci"
        for index in sa.inspect(bind).get_indexes("usuarios")
    ):
        op.create_index(
            "uq_usuarios_email_ci", "usuarios", [sa.text("lower(email)")], unique=True
        )

    if not sa.inspect(bind).has_table("produtos"):
        op.create_table(
            "produtos",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("sabor", sa.String(length=80), nullable=False),
            sa.Column("tamanho", sa.String(length=1), nullable=False),
            sa.Column("preco", sa.Float(), nullable=False),
            sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.UniqueConstraint("sabor", "tamanho", name="uq_produto_sabor_tamanho"),
        )

    produtos = sa.table(
        "produtos",
        sa.column("sabor", sa.String),
        sa.column("tamanho", sa.String),
        sa.column("preco", sa.Float),
        sa.column("ativo", sa.Boolean),
    )
    if bind.execute(sa.text("SELECT count(*) FROM produtos")).scalar_one() == 0:
        op.bulk_insert(
            produtos,
            [
                {"sabor": sabor, "tamanho": tamanho, "preco": preco, "ativo": True}
                for sabor, precos in {
                    "Calabresa": {"P": 32.90, "M": 42.90, "G": 52.90},
                    "Margherita": {"P": 29.90, "M": 39.90, "G": 49.90},
                    "Quatro Queijos": {"P": 36.90, "M": 46.90, "G": 56.90},
                }.items()
                for tamanho, preco in precos.items()
            ],
        )

    if "criado_em" not in {column["name"] for column in sa.inspect(bind).get_columns("pedidos")}:
        op.add_column(
            "pedidos",
            sa.Column("criado_em", sa.DateTime(timezone=True), nullable=True),
        )
    op.execute(sa.text("UPDATE pedidos SET criado_em = CURRENT_TIMESTAMP WHERE criado_em IS NULL"))
    if not any(
        index["name"] == "ix_pedidos_usuario_criado_em"
        for index in sa.inspect(bind).get_indexes("pedidos")
    ):
        op.create_index("ix_pedidos_usuario_criado_em", "pedidos", ["usuario", "criado_em"])

    itens_columns = {column["name"] for column in sa.inspect(bind).get_columns("itens_pedido")}
    if "produto_id" not in itens_columns:
        op.add_column(
            "itens_pedido",
            sa.Column("produto_id", sa.Integer(), nullable=True),
        )
    produto_fk_exists = any(
        foreign_key.get("referred_table") == "produtos"
        and foreign_key.get("constrained_columns") == ["produto_id"]
        for foreign_key in sa.inspect(bind).get_foreign_keys("itens_pedido")
    )
    if not produto_fk_exists:
        with op.batch_alter_table("itens_pedido") as batch_op:
            batch_op.create_foreign_key(
                "fk_itens_pedido_produtos", "produtos", ["produto_id"], ["id"]
            )


def downgrade() -> None:
    with op.batch_alter_table("itens_pedido") as batch_op:
        batch_op.drop_constraint("fk_itens_pedido_produtos", type_="foreignkey")
        batch_op.drop_column("produto_id")
    op.drop_index("ix_pedidos_usuario_criado_em", table_name="pedidos")
    op.drop_column("pedidos", "criado_em")
    op.drop_table("produtos")
    op.drop_index("uq_usuarios_email_ci", table_name="usuarios")
