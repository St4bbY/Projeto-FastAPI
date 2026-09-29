# Projeto FastAPI

API de pedidos de uma pizzaria, feita para praticar Python, FastAPI e SQLAlchemy. Dá para criar uma conta, consultar o cardápio e acompanhar os próprios pedidos. Não há interface web: as requisições podem ser feitas pelo Swagger em `/docs`.

## Rodar no Windows

Com Python 3.11 ou superior instalado, clone o projeto e prepare o ambiente:

```powershell
git clone https://github.com/St4bbY/Projeto-FastAPI.git
cd Projeto-FastAPI
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

Gere uma chave para os tokens e coloque o resultado no campo `SECRET_KEY` do `.env`:

```powershell
py -c "import secrets; print(secrets.token_urlsafe(48))"
```

Crie as tabelas e carregue o cardápio inicial com as migrações:

```powershell
alembic upgrade head
```

Agora inicie a API:

```powershell
uvicorn main:app --reload
```

Abra `http://127.0.0.1:8000/docs`. O banco local é SQLite e fica no arquivo `banco.db`.

## Usar a API

Primeiro, crie uma conta em `POST /auth/criar_conta`:

```json
{
  "nome": "Ana Silva",
  "email": "ana@example.com",
  "senha": "minha-senha-segura"
}
```

Entre em `POST /auth/login` com o mesmo email e senha. Copie o `access_token` da resposta e use o botão **Authorize** no Swagger para acessar as rotas protegidas.

O cardápio está em `GET /pedidos/catalogo`. Para criar um pedido, envie os IDs dos produtos e as quantidades para `POST /pedidos/`:

```json
{
  "itens": [
    {"produto_id": 1, "quantidade": 2},
    {"produto_id": 5, "quantidade": 1}
  ]
}
```

O servidor busca os preços no catálogo e calcula o total. Assim, o valor não depende do que o cliente enviar. O cardápio inicial tem três sabores em tamanhos P, M e G; não há ainda uma tela ou rota administrativa para editar preços.

## Rotas disponíveis

| Método | Rota | Para que serve |
| --- | --- | --- |
| `GET` | `/` | Verificar se a API está rodando |
| `POST` | `/auth/criar_conta` | Criar uma conta |
| `POST` | `/auth/login` | Entrar e receber um token |
| `GET` | `/auth/me` | Ver os dados da conta autenticada |
| `GET` | `/pedidos/catalogo` | Consultar sabores, tamanhos e preços |
| `POST` | `/pedidos/` | Criar um pedido |
| `GET` | `/pedidos/` | Listar pedidos, com paginação |
| `GET` | `/pedidos/{id}` | Consultar um pedido |
| `PATCH` | `/pedidos/{id}/cancelar` | Cancelar um pedido pendente |

As rotas de pedidos mostram apenas os pedidos do usuário autenticado. A listagem aceita `limite` (de 1 a 100) e `deslocamento` (a partir de 0).

## Testes

Os testes usam um banco em memória, sem mexer no `banco.db` local:

```powershell
pytest
```

As dependências de desenvolvimento, incluindo pytest, estão em `requirements-dev.txt`.

## Configuração

`SECRET_KEY` é obrigatória. Para apontar a API a outro banco compatível com SQLAlchemy, defina `DATABASE_URL` no `.env`. Mantenha `.env` e `banco.db` fora do Git; ambos já estão no `.gitignore`.
