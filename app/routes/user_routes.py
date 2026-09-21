from typing import Optional
from fastapi import APIRouter, Depends, Response
from app.dependencies.user_dependencies import obtener_usuario_o_404
from app.schemas.user_schemas import User, UserCreate, UserUpdate, UserPatch
from app.services.user_services import (
    actualizar_usuario,
    actualizar_usuario_parcial,
    eliminar_usuario,
    listar_usuarios,
    registrar_usuario
)

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.get(
    "", 
    response_model=list[User],
    summary="Listar y filtrar usuarios",
    description=(
        "Obtiene los usuarios registrados. permitiendo filtrar por rol "
        " y por estado activo; ambos filtros pueden combinarse."
    ),
    response_description="Lista de usuarios que cumplen los filtros"
)
def obtener_usuarios(
    role: Optional[str] = None,
    is_active: Optional[bool] = None
):
    return  listar_usuarios(
        role=role,
        is_active=is_active
    )

@router.get(
    "/{user_id}", 
    response_model=User,
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
    response_model=User,
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
def crear_usuario(usuario: UserCreate):
    return registrar_usuario(usuario)

@router.put(
    "/{user_id}",
    response_model=User,
    status_code=200,
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
    usuario: User = Depends(obtener_usuario_o_404)  
):
    return actualizar_usuario(
        usuario_actual=usuario,
        datos=datos
    )

@router.patch(
    "/{user_id}",
    response_model=User,
    status_code=200,
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
    usuario: User = Depends(obtener_usuario_o_404)
):
    return actualizar_usuario_parcial(
        usuario_actual=usuario,
        datos=datos
    )
    
@router.delete(
    "/{user_id}",
    status_code=204,
    summary="Eliminar un usuario",
    description="Elimina de la colección en memoria el usuario indicado.",
    response_description="Usuario eliminado; respuesta sin cuerpo",
    responses={
        404: {"description": "Usuario no encontrado"}
    }
)
def eliminar_usuario_endpoint(
    usuario: User = Depends(obtener_usuario_o_404)
):
    eliminar_usuario(usuario)
    return Response(status_code=204)