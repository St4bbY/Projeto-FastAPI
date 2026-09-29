# API de pedidos

API REST para cadastro de usuários e criação de pedidos, construída com Python, FastAPI, SQLAlchemy e SQLite. As senhas são armazenadas com hash bcrypt e o login retorna um token JWT.

## Requisitos

- Python 3.10 ou superior
- pip

## Executar localmente

No PowerShell, na pasta do projeto:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Gere uma chave para `SECRET_KEY` e substitua o valor de exemplo no `.env`:

```powershell
py -c "import secrets; print(secrets.token_urlsafe(48))"
```

Inicie a API:

```powershell
uvicorn main:app --reload
```

Abra `http://127.0.0.1:8000/docs` para explorar os endpoints.

## Endpoints principais

- `POST /auth/criar_conta` — cria uma conta.
- `POST /auth/login` — valida email e senha e retorna um JWT válido por 30 minutos.
- `GET /auth/me` — retorna os dados do usuário autenticado.
- `POST /pedidos/pedido` — cria um pedido para o usuário autenticado.

Para endpoints autenticados, envie `Authorization: Bearer <token>`. No Swagger, use **Authorize**.

## Segurança

Não publique `.env`, `.venv/` ou `banco.db`. O `.gitignore` já exclui esses arquivos. Configure `SECRET_KEY` separadamente em cada ambiente e nunca use a chave de exemplo em produção.
