from fastapi import APIRouter, Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth.auth_service import (
    authenticate_user,
    register_user,
)
from app.auth.security import create_access_token
from app.dependencies.auth_dependency import get_current_active_user
from app.dependencies.database_dependency import get_db
from app.models.user_model import User
from app.schemas.auth_schema import Token, UserRegister
from app.schemas.user_schemas import UserResponse
from app.rate_limit import limiter


router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
    summary="Registrar una cuenta",
    responses={
        400: {"description": "Correo registrado"},
        422: {"description": "Datos de registro invalidos"},
        429: {"description": "Límite de solicitudes excedido."}
    }
)
@limiter.limit("3/minute")
def register(
    request: Request,
    datos: UserRegister,
    db: Session = Depends(get_db),
):
    return register_user(db, datos)


@router.post(
    "/login",
    response_model=Token,
    summary="Iniciar sesion",
    description=(
        "Introduce el correo en username y la contraseña "
        "en password para obtener un token."
    ),
    responses={
        401: {"description": "Credenciales incorrectas"},
        403: {"description": "Usuario inactivo"},
        429: {"description": "Límite de solicitudes excedido."}
    }
)
@limiter.limit("5/minute")
def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    usuario = authenticate_user(
        db,
        form_data.username,
        form_data.password,
    )

    token = create_access_token(
        {"sub": str(usuario.id)}
    )

    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"

    return Token(access_token=token)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Consultar mi cuenta",
    responses={
        401: {"description": "Token ausente, invalido o vencido"},
        403: {"description": "Usuario inactivo"},
    },
)
def me(
    usuario: User = Depends(get_current_active_user),
):
    return usuario