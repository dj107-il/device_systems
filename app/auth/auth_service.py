from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.security import (
    get_password_hash,
    verify_password,
)
from app.models.user_model import User
from app.schemas.auth_schema import UserRegister


def register_user(db: Session, datos: UserRegister) -> User:
    existente = db.scalar(
        select(User).where(User.email == str(datos.email))
    )

    if existente is not None:
        raise HTTPException(
            status_code=400,
            detail="El correo ya esta registrado.",
        )

    usuario = User(
        name=datos.name,
        email=str(datos.email),
        hashed_password=get_password_hash(
            datos.password.get_secret_value()
        ),
        role="user",
        is_active=True,
    )

    db.add(usuario)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="No se pudo registrar el usuario. Comprueba el correo.",
        )

    db.refresh(usuario)
    return usuario


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> User:
    usuario = db.scalar(
        select(User).where(User.email == email.strip())
    )

    error = HTTPException(
        status_code=401,
        detail="Correo o contraseña incorrectos.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if usuario is None:
        raise error

    if not verify_password(password, usuario.hashed_password):
        raise error

    if not usuario.is_active:
        raise HTTPException(
            status_code=403,
            detail="El usuario esta inactivo.",
        )

    return usuario