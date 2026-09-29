from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from auth_dependencies import usuario_atual
from dependencies import pegar_sessao
from models import Usuario
from schemas import LoginSchema, TokenResposta, UsuarioCriar, UsuarioPublico
from security import bcrypt_context, criar_token

auth_router = APIRouter(prefix="/auth", tags=["Autenticação"])


@auth_router.post(
    "/criar_conta",
    response_model=UsuarioPublico,
    status_code=status.HTTP_201_CREATED,
    summary="Criar conta",
)
def criar_conta(dados: UsuarioCriar, session: Session = Depends(pegar_sessao)):
    email = str(dados.email).lower()
    existente = session.query(Usuario).filter(Usuario.email == email).first()
    if existente:
        raise HTTPException(status_code=409, detail="Este e-mail já está cadastrado")

    usuario = Usuario(
        dados.nome.strip(),
        email,
        bcrypt_context.hash(dados.senha),
        ativo=True,
        admin=False,
    )
    session.add(usuario)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="Este e-mail já está cadastrado")
    session.refresh(usuario)
    return usuario


@auth_router.post("/login", response_model=TokenResposta, summary="Entrar")
def login(dados: LoginSchema, session: Session = Depends(pegar_sessao)):
    email = str(dados.email).lower()
    usuario = session.query(Usuario).filter(Usuario.email == email).first()
    senha_valida = usuario is not None and bcrypt_context.verify(dados.senha, usuario.senha)
    if not senha_valida or not usuario.ativo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenResposta(access_token=criar_token(usuario.id))


@auth_router.get("/me", response_model=UsuarioPublico, summary="Ver minha conta")
def meu_usuario(usuario: Usuario = Depends(usuario_atual)):
    return usuario
