from typing import Literal
from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session
from app.rate_limit import limiter

from app.dependencies.database_dependency import get_db
from app.dependencies.user_dependencies import obtener_usuario_o_404
from app.schemas.loan_schema import LoanDetailResponse
from app.services import loan_services
from app.models.user_model import User
from app.schemas.user_schemas import UserCreate, UserUpdate, UserPatch, UserResponse
from app.services.user_services import (
    actualizar_usuario,
    actualizar_usuario_parcial,
    eliminar_usuario,
    listar_usuarios,
    registrar_usuario
)
from app.dependencies.auth_dependency import (
    get_current_active_user,
    require_admin,
    require_admin_or_support
)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(get_current_active_user)],
    responses={
        401: {
            "description": "Token ausente, inválido o vencido."
        },
        403: {
            "description": "Usuario inactivo o sin permisos suficientes."
        }
    }
)

@router.get(
    "", 
    response_model=list[UserResponse],
    summary="Listar y filtrar usuarios",
    description=(
        "Obtiene los usuarios registrados. permitiendo filtrar por rol "
        " y por estado activo; ambos filtros pueden combinarse."
    ),
    response_description="Lista de usuarios que cumplen los filtros",
    responses={
        429: {"description": "Límite de solicitudes excedido."}
    }
)
@limiter.limit("30/minute")
def obtener_usuarios(
    request: Request,
    role: Literal["admin", "support", "user"] | None = None,
    is_active: bool | None = None,
    ordenar_por: Literal["name", "created_at"] = "name",
    db: Session = Depends(get_db)
):
    return  listar_usuarios(
        db=db,
        role=role,
        is_active=is_active,
        ordenar_por= ordenar_por
    )

@router.get(
    "/{user_id}", 
    response_model=UserResponse,
    summary="Consultar un usuario",
    description="Buscar un usuario por su identificador.(id)",
    response_description="Usuario encontrado",
    responses={
        404: {"description": "Usuario no encontrado"}
    }
)
def obtener_usuario(
    usuario: User = Depends(obtener_usuario_o_404)
):
    return usuario


@router.post(
    "/",
    dependencies=[Depends(require_admin)], #Permiso adicional
    response_model=UserResponse,
    status_code=201,
    summary="crea un usuario",
    description=(
        "Registra un usuario y genera su identificador. "
        "El correo no debe estar registrado."
    ),
    response_description="Usuario creado",
    responses={
        400: {"description": "Correo electrónico duplicado"}
    }
)
def crear_usuario(
    datos: UserCreate,
    db: Session = Depends(get_db)
):
    return registrar_usuario(db, datos)

@router.put(
    "/{user_id}",
    dependencies=[Depends(require_admin)],
    response_model=UserResponse,
    summary="Actualizar completamente un usuario",
    description=(
        "Reemplaza nombre, correo, rol y estado del usuario. "
        "Todos esos campos son obligatorios. Conserva el identificador."
    ),
    response_description="Usuario actualizado",
    responses={
        400: {"description": "El correo pertenece a otro usuario"},
        404: {"description": "Usuario no encontrado"}
    }
)
def actualizar_usuario_endpoint(
    datos: UserUpdate,
    usuario: User = Depends(obtener_usuario_o_404),
    db: Session = Depends(get_db)
):
    return actualizar_usuario(
        db=db,
        usuario_actual=usuario,
        datos=datos
    )

@router.patch(
    "/{user_id}",
    dependencies=[Depends(require_admin)],
    response_model=UserResponse,
    summary="Actualizar parcialmente un usuario",
    description="Modifica únicamente los campos enviados. Debe incluir al menos uno. \n No permite valores null, ni correos de otros usuarios.",
    response_description="Usuario actualizado",
    responses={
        400: {"description": "Actualización vacía o correo duplicado"},
        404: {"description": "Usuario no encontrado"},
        422: {"description": "Datos invalidos o campos con valor null"}
    }
)
def actualizar_usuario_parcial_endpoint(
    datos: UserPatch,
    usuario: User = Depends(obtener_usuario_o_404),
    db: Session = Depends(get_db)
):
    return actualizar_usuario_parcial(
        db=db,
        usuario_actual=usuario,
        datos=datos
    )
    
@router.delete(
    "/{user_id}",
    dependencies=[Depends(require_admin)],
    status_code=204,
    summary="Eliminar un usuario",
    description="Elimina un usuario que no tenga historial de préstamos.",
    response_description="Usuario eliminado; respuesta sin cuerpo",
    responses={
        400: {"description": "Restricción de integridad incumplida."},
        404: {"description": "Usuario no encontrado"},
        409: {"description": "El usuario tiene préstamos registrados"}
    }
)
def eliminar_usuario_endpoint(
    usuario: User = Depends(obtener_usuario_o_404),
    db: Session = Depends(get_db)
):
    eliminar_usuario(db, usuario)
    return Response(status_code=204)

@router.get(
    "/{user_id}/loans",
    dependencies=[Depends(require_admin_or_support)],
    response_model=list[LoanDetailResponse],
    summary="Consultar préstamos de un usuario",
    description="Muestra el historial del usuario y los dispositivos asociados.",
    response_description="Historial de préstamos del usuario",
    responses={404: {"description": "Usuario inexistente"}}
)
def obtener_prestamos_usuario(
    usuario: User = Depends(obtener_usuario_o_404),
    db: Session = Depends(get_db)
):
    return loan_services.listar_prestamos(
        db=db,
        user_id=usuario.id
    )