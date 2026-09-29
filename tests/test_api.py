def criar_usuario_e_token(client, email="ana@example.com"):
    cadastrado = client.post(
        "/auth/criar_conta",
        json={"nome": "Ana Silva", "email": email, "senha": "senha-segura-123"},
    )
    assert cadastrado.status_code == 201
    login = client.post(
        "/auth/login",
        json={"email": email, "senha": "senha-segura-123"},
    )
    assert login.status_code == 200
    return login.json()["access_token"]


def test_health_and_catalog(client):
    assert client.get("/").json()["status"] == "ok"
    catalogo = client.get("/pedidos/catalogo")
    assert catalogo.status_code == 200
    assert len(catalogo.json()) == 2
    assert catalogo.json()[0]["preco"] > 0


def test_register_login_and_duplicate_email(client):
    criar_usuario_e_token(client, email="Ana@Example.com")

    duplicado = client.post(
        "/auth/criar_conta",
        json={"nome": "Outra Ana", "email": "ana@example.com", "senha": "senha-segura-123"},
    )
    assert duplicado.status_code == 409

    login_invalido = client.post(
        "/auth/login",
        json={"email": "ana@example.com", "senha": "senha-errada"},
    )
    assert login_invalido.status_code == 401


def test_order_total_comes_from_catalog_and_can_be_cancelled(client):
    token = criar_usuario_e_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    sem_itens = client.post("/pedidos/", headers=headers, json={"itens": []})
    assert sem_itens.status_code == 422
    quantidade_excessiva = client.post(
        "/pedidos/",
        headers=headers,
        json={"itens": [{"produto_id": 1, "quantidade": 20}] * 2},
    )
    assert quantidade_excessiva.status_code == 422

    pedido = client.post(
        "/pedidos/",
        headers=headers,
        json={"itens": [{"produto_id": 1, "quantidade": 2}, {"produto_id": 2, "quantidade": 1}]},
    )
    assert pedido.status_code == 201
    conteudo = pedido.json()
    assert conteudo["preco"] == 105.7
    assert conteudo["status"] == "PENDENTE"
    assert len(conteudo["itens"]) == 2
    assert conteudo["criado_em"]

    pagina = client.get("/pedidos/?limite=1&deslocamento=0", headers=headers)
    assert pagina.status_code == 200
    assert pagina.json()["total"] == 1
    assert pagina.json()["limite"] == 1

    cancelado = client.patch(f"/pedidos/{conteudo['id']}/cancelar", headers=headers)
    assert cancelado.status_code == 200
    assert cancelado.json()["status"] == "CANCELADO"

    cancelar_de_novo = client.patch(f"/pedidos/{conteudo['id']}/cancelar", headers=headers)
    assert cancelar_de_novo.status_code == 409


def test_user_cannot_read_another_users_order(client):
    token_ana = criar_usuario_e_token(client, email="ana@example.com")
    pedido = client.post(
        "/pedidos/",
        headers={"Authorization": f"Bearer {token_ana}"},
        json={"itens": [{"produto_id": 1, "quantidade": 1}]},
    ).json()

    token_bruno = criar_usuario_e_token(client, email="bruno@example.com")
    response = client.get(
        f"/pedidos/{pedido['id']}",
        headers={"Authorization": f"Bearer {token_bruno}"},
    )
    assert response.status_code == 404


def test_private_routes_reject_missing_token(client):
    assert client.get("/pedidos/").status_code == 401
    assert client.get("/auth/me").status_code == 401
