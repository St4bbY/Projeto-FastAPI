from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dependencies import pegar_sessao
from models import Usuario
from schemas import LoginSchema, UsuarioSchema
from security import bcrypt_context, criar_token
from auth_dependencies import usuario_atual

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.get("/")
async def home():
    return {"mensagem": "Rota de autenticação", "autenticado": False}


@auth_router.post("/criar_conta")
async def criar_conta(usuario_schema: UsuarioSchema, session: Session = Depends(pegar_sessao)):
    usuario = session.query(Usuario).filter(Usuario.email == usuario_schema.email).first()
    if usuario:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    senha_criptografada = bcrypt_context.hash(usuario_schema.senha)
    novo_usuario = Usuario(
        usuario_schema.nome,
        usuario_schema.email,
        senha_criptografada,
        True,
        False,
    )
    session.add(novo_usuario)
    session.commit()
    return {"mensagem": f"Usuário {usuario_schema.email} criado com sucesso"}


@auth_router.post("/login")
async def login(login_schema: LoginSchema, session: Session = Depends(pegar_sessao)):
    usuario = session.query(Usuario).filter(Usuario.email == login_schema.email).first()
    if not usuario or not bcrypt_context.verify(login_schema.senha, usuario.senha):
        raise HTTPException(status_code=401, detail="E-mail ou senha inválidos")

    access_token = criar_token(usuario.id)
    return {"access_token": access_token, "token_type": "bearer"}


@auth_router.get("/me")
async def meu_usuario(usuario: Usuario = Depends(usuario_atual)):
    return {"id": usuario.id, "nome": usuario.nome, "email": usuario.email}
