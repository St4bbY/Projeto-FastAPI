from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from models import Usuario
from security import decodificar_token
from dependencies import pegar_sessao

bearer_scheme = HTTPBearer(auto_error=False)


def usuario_atual(
    credenciais: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session: Session = Depends(pegar_sessao),
) -> Usuario:
    if credenciais is None:
        raise HTTPException(status_code=401, detail="Token Bearer obrigat\u00f3rio")
    try:
        payload = decodificar_token(credenciais.credentials)
        id_usuario = int(payload["sub"])
    except (JWTError, KeyError, TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Token inv\u00e1lido ou expirado")

    usuario = session.query(Usuario).filter(Usuario.id == id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=401, detail="Usu\u00e1rio do token n\u00e3o existe")
    return usuario
