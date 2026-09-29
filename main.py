from fastapi import FastAPI

from auth_routes import auth_router
from order_routes import order_router


app = FastAPI(
    title="Pedidos da Pizzaria",
    description="API para criar uma conta, consultar o cardápio e acompanhar pedidos.",
    version="0.1.0",
)

app.include_router(auth_router)
app.include_router(order_router)


@app.get("/", tags=["status"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "servico": "Pedidos da Pizzaria", "documentacao": "/docs"}
