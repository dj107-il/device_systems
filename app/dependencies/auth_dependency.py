from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.auth.security import decode_access_token
from app.dependencies.database_dependency import get_db
from app.models.user_model import User


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    error = HTTPException(
        status_code=401,
        detail="No se pudieron validar las credenciales.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        user_id = int(payload["sub"])

        if user_id <= 0:
            raise ValueError("Identificador invalido")

    except (JWTError, ValueError, TypeError, KeyError):
        raise error

    usuario = db.get(User, user_id)

    if usuario is None:
        raise error

    return usuario


def get_current_active_user(
    usuario: User = Depends(get_current_user),
) -> User:
    if not usuario.is_active:
        raise HTTPException(
            status_code=403,
            detail="El usuario esta inactivo.",
        )

    return usuario


def require_admin(
    usuario: User = Depends(get_current_active_user),
) -> User:
    if usuario.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Se requiere el rol admin.",
        )

    return usuario


def require_admin_or_support(
    usuario: User = Depends(get_current_active_user),
) -> User:
    if usuario.role not in ("admin", "support"):
        raise HTTPException(
            status_code=403,
            detail="Se requiere el rol admin o support.",
        )

    return usuario