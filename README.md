# API de Pedidos

API REST para cadastro de clientes e gerenciamento de pedidos, construída com FastAPI, SQLAlchemy e SQLite. A API oferece autenticação JWT, hashes bcrypt, catálogo de pizzas e pedidos com itens e preços calculados no servidor.

## Funcionalidades

- Cadastro e login com validação e email único sem distinção entre maiúsculas e minúsculas.
- JWT com validade de 30 minutos e rota para consultar o usuário autenticado.
- Catálogo de produtos com preços definidos no servidor.
- Criação de pedidos com itens, quantidades e total calculado pela API.
- Consulta paginada dos próprios pedidos e consulta por identificador.
- Cancelamento de pedidos pendentes e registro de data de criação.
- Migrações de banco gerenciadas pelo Alembic.
- Testes de autenticação, catálogo, pedidos, paginação e controle de acesso.

## Tecnologias

Python · FastAPI · SQLAlchemy · SQLite · Alembic · Pydantic · JWT · bcrypt · pytest

## Requisitos

- Python 3.11 ou superior
- pip

## Instalação no Windows (PowerShell)

```powershell
git clone https://github.com/St4bbY/Projeto-FastAPI.git
cd Projeto-FastAPI
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

Gere uma chave secreta:

```powershell
py -c "import secrets; print(secrets.token_urlsafe(48))"
```

Cole a chave em `SECRET_KEY` no arquivo `.env`. Não publique `.env`.

## Banco de dados e execução

Execute as migrações para criar ou atualizar o banco:

```powershell
alembic upgrade head
```

Inicie a API:

```powershell
uvicorn main:app --reload
```

A API fica em `http://127.0.0.1:8000`; o status está em `/`, a documentação interativa em `/docs` e a documentação alternativa em `/redoc`.

## Fluxo rápido

1. Crie uma conta em `POST /auth/criar_conta`:

```json
{
  "nome": "Ana Silva",
  "email": "ana@example.com",
  "senha": "minha-senha-segura"
}
```

2. Faça login em `POST /auth/login` e copie `access_token`.
3. No botão **Authorize** da página `/docs`, informe `Bearer <access_token>`.
4. Consulte `GET /pedidos/catalogo` para ver os produtos e seus IDs.
5. Crie um pedido em `POST /pedidos/`:

```json
{
  "itens": [
    {"produto_id": 1, "quantidade": 2},
    {"produto_id": 5, "quantidade": 1}
  ]
}
```

O preço vem do catálogo. O cliente não envia nem escolhe o total do pedido.

## Endpoints

| Método | Caminho | Acesso | Descrição |
| --- | --- | --- | --- |
| `GET` | `/` | Público | Status da API |
| `POST` | `/auth/criar_conta` | Público | Criar conta |
| `POST` | `/auth/login` | Público | Obter token JWT |
| `GET` | `/auth/me` | JWT | Consultar conta atual |
| `GET` | `/pedidos/catalogo` | Público | Listar produtos e preços |
| `POST` | `/pedidos/` | JWT | Criar pedido com itens do catálogo |
| `GET` | `/pedidos/?deslocamento=0&limite=20` | JWT | Listar pedidos paginados |
| `GET` | `/pedidos/{id}` | JWT | Consultar pedido próprio |
| `PATCH` | `/pedidos/{id}/cancelar` | JWT | Cancelar pedido pendente |

A paginação aceita `limite` entre 1 e 100 e `deslocamento` a partir de 0. Cada usuário só pode acessar os próprios pedidos.

## Testes

Instale as dependências de desenvolvimento e rode:

```powershell
pip install -r requirements-dev.txt
pytest
```

Os testes usam um banco SQLite em memória e não alteram `banco.db`.

## Configuração

- `SECRET_KEY`: chave privada obrigatória para assinar JWTs.
- `DATABASE_URL`: endereço do banco; o padrão local é `sqlite:///banco.db`.

Senhas, banco local e ambiente virtual são ignorados pelo Git. Não use a chave de exemplo em produção.
