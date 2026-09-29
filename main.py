from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="API de Pedidos",
    description="API para cadastro de clientes e gerenciamento dos próprios pedidos.",
    version="1.0.0",
)

from auth_routes import auth_router
from order_routes import order_router

app.include_router(auth_router)
app.include_router(order_router)


@app.get("/", tags=["status"])
async def health_check():
    return {"status": "ok", "servico": "API de Pedidos", "documentacao": "/docs"}
