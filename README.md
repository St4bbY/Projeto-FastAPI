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

Gere uma chave para `SECRET_KEY` e substitua o valor de exemplo no `.env`. Por exemplo:

```powershell
py -c "import secrets; print(secrets.token_urlsafe(48))"
```

Inicie a API:

```powershell
uvicorn main:app --reload
```

Abra `http://127.0.0.1:8000/docs` para explorar e chamar os endpoints.

## Endpoints principais

- `POST /auth/criar_conta` — cria uma conta.
- `POST /auth/login` — valida email e senha e retorna um JWT com validade de 30 minutos.
- `GET /auth/me` — retorna os dados do usuário autenticado.
- `POST /pedidos/pedido` — cria um pedido para o usuário autenticado.

Para endpoints autenticados, envie o cabeçalho `Authorization: Bearer <token>`. No Swagger, use o botão **Authorize**.

## Publicar no GitHub

Crie um repositório vazio no GitHub. Depois, na pasta do projeto, execute:

```powershell
git init
git add .
git status
git commit -m "feat: primeira versão da API de pedidos"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/SEU-REPOSITORIO.git
git push -u origin main
```

Antes do commit, confira `git status`: `.env`, `.venv/` e `banco.db` não devem aparecer. O `.gitignore` do projeto já exclui esses arquivos. Nunca publique segredos reais; configure `SECRET_KEY` separadamente no serviço onde hospedar a API.
