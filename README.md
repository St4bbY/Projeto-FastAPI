# API de Pedidos

API REST para cadastro de clientes e gerenciamento de pedidos. O projeto usa FastAPI, SQLAlchemy, SQLite, autenticação JWT e hashes bcrypt para senhas.

## Funcionalidades

- Cadastro com validação de nome, email e senha.
- Login com JWT de 30 minutos e rota para consultar a conta autenticada.
- Criação, listagem e consulta dos próprios pedidos.
- Cancelamento de pedidos enquanto estiverem pendentes.
- Validação de dados e documentação interativa gerada pelo FastAPI.
- Criação automática das tabelas ao iniciar em um banco novo.

## Tecnologias

Python · FastAPI · SQLAlchemy · SQLite · Alembic · Pydantic · JWT · bcrypt

## Requisitos

- Python 3.11 ou superior
- pip

## Instalação no Windows (PowerShell)

Clone o repositório e entre na pasta:

```powershell
git clone https://github.com/St4bbY/Projeto-FastAPI.git
cd Projeto-FastAPI
```

Crie e ative o ambiente virtual e instale as dependências:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Configure a chave JWT:

```powershell
Copy-Item .env.example .env
py -c "import secrets; print(secrets.token_urlsafe(48))"
```

Copie a chave gerada para `SECRET_KEY` no arquivo `.env`. Não publique esse arquivo.

## Iniciar

```powershell
uvicorn main:app --reload
```

A API fica em `http://127.0.0.1:8000`. A página `/` informa o status; a documentação interativa está em `/docs` e a documentação alternativa em `/redoc`.

## Fluxo rápido

1. Crie uma conta em `POST /auth/criar_conta`:

```json
{
  "nome": "Ana Silva",
  "email": "ana@example.com",
  "senha": "minha-senha-segura"
}
```

2. Faça login em `POST /auth/login` usando o mesmo email e senha. Copie `access_token` da resposta.
3. No botão **Authorize** do `/docs`, informe `Bearer <access_token>`.
4. Crie um pedido em `POST /pedidos/`:

```json
{
  "preco": 42.5
}
```

O usuário do pedido vem do token autenticado. Use `GET /pedidos/` para listar seus pedidos, `GET /pedidos/{id}` para consultar um e `PATCH /pedidos/{id}/cancelar` para cancelar um pedido pendente.

## Endpoints

| Método | Caminho | Acesso | Descrição |
| --- | --- | --- | --- |
| `GET` | `/` | Público | Status da API |
| `POST` | `/auth/criar_conta` | Público | Cadastrar conta |
| `POST` | `/auth/login` | Público | Obter token JWT |
| `GET` | `/auth/me` | JWT | Consultar conta atual |
| `POST` | `/pedidos/` | JWT | Criar pedido |
| `GET` | `/pedidos/` | JWT | Listar os próprios pedidos |
| `GET` | `/pedidos/{id}` | JWT | Consultar pedido próprio |
| `PATCH` | `/pedidos/{id}/cancelar` | JWT | Cancelar pedido pendente |

## Configuração

- `SECRET_KEY`: chave privada para assinar os tokens. Obrigatória; gere uma chave diferente para cada ambiente.
- `DATABASE_URL`: endereço do banco. O padrão local é `sqlite:///banco.db`.

## Segurança e dados locais

Senhas nunca são retornadas pela API e são armazenadas com bcrypt. Tokens expiram em 30 minutos. Cada conta só pode consultar e cancelar os próprios pedidos. O arquivo `.gitignore` exclui `.env`, ambientes virtuais e o banco SQLite local.

## Melhorias futuras

- Catálogo de produtos e itens vinculados a cada pedido.
- Testes automatizados para autenticação e pedidos.
- Deploy público com banco de dados gerenciado.
