from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.dependencies.database_dependency import get_db
from app.schemas.device_schemas import (
    DeviceCreate,
    DevicePatch,
    DeviceResponse,
    DeviceType,
    DeviceUpdate,
)
from app.services import device_services
from app.schemas.loan_schema import LoanDetailResponse
from app.services import loan_services
from app.dependencies.auth_dependency import (
    get_current_active_user,
    require_admin,
    require_admin_or_support,
)


router = APIRouter(
    prefix="/devices",
    tags=["Devices"],
    dependencies=[Depends(get_current_active_user)],
    responses={
        401: {
            "description": "Token ausente, inváliddo o vencido."
        },
        403: {
            "description": "Usuario inactivo o sin permisos suficientes."
        }
    }
)


@router.get(
    "",
    response_model=list[DeviceResponse],
    summary="Listar dispositivos",
    description=(
        "Lista dispositivos y permite combinar filtros por tipo, "
        "disponibilidad, marca y búsqueda en nombre o serie."
    ),
    response_description="Lista de dispositivos",
    responses={422: {"description": "Filtros inválidos"}}
)
def obtener_dispositivos(
    device_type: DeviceType | None = None,
    is_available: bool | None = None,
    brand: str | None = Query(default=None, min_length=1, max_length=50),
    search: str | None = Query(default=None, min_length=1, max_length=100),
    db: Session = Depends(get_db)
):
    return device_services.listar_dispositivos(
        db,
        device_type,
        is_available,
        brand,
        search
    )


@router.get(
    "/{device_id}",
    response_model=DeviceResponse,
    summary="Consultar un dispositivo",
    response_description="Dispositivo encontrado",
    responses={404: {"description": "Dispositivo inexistente"}}
)
def obtener_dispositivo(
    device_id: int,
    db: Session = Depends(get_db)
):
    return device_services.buscar_dispositivo_por_id(db, device_id)


@router.post(
    "",
    dependencies=[Depends(require_admin_or_support)],
    response_model=DeviceResponse,
    status_code=201,
    summary="Crear un dispositivo",
    description="Registra un dispositivo con número de serie único.",
    response_description="Dispositivo creado",
    responses={
        400: {"description": "Serie duplicada"},
        422: {"description": "Datos inválidos"}
    }
)
def crear_dispositivo(
    datos: DeviceCreate,
    db: Session = Depends(get_db)
):
    return device_services.registrar_dispositivo(db, datos)


@router.put(
    "/{device_id}",
    dependencies=[Depends(require_admin_or_support)],
    response_model=DeviceResponse,
    summary="Actualizar completamente un dispositivo",
    description="Exige todos los campos editables; conserva ID y fecha.",
    response_description="Dispositivo actualizado",
    responses={
        400: {"description": "Serie duplicada"},
        404: {"description": "Dispositivo inexistente"},
        409: {"description": "Disponibilidad incompatible con un préstamo"},
        422: {"description": "Datos inválidos o incompletos"}
    }
)
def actualizar_dispositivo(
    device_id: int,
    datos: DeviceUpdate,
    db: Session = Depends(get_db)
):
    dispositivo = device_services.buscar_dispositivo_por_id(db, device_id)

    return device_services.actualizar_dispositivo(
        db, dispositivo, datos
    )


@router.patch(
    "/{device_id}",
    dependencies=[Depends(require_admin_or_support)],
    response_model=DeviceResponse,
    summary="Actualizar parcialmente un dispositivo",
    description="Modifica los campos enviados. Solo brand permite null.",
    response_description="Dispositivo actualizado",
    responses={
        400: {"description": "Serie duplicada o actualización vacía"},
        404: {"description": "Dispositivo inexistente"},
        409: {"description": "Disponibilidad incompatible con un préstamo"},
        422: {"description": "Datos inválidos"}
    }
)
def actualizar_dispositivo_parcial(
    device_id: int,
    datos: DevicePatch,
    db: Session = Depends(get_db)
):
    dispositivo = device_services.buscar_dispositivo_por_id(db, device_id)

    return device_services.actualizar_dispositivo_parcial(
        db, dispositivo, datos
    )

@router.delete(
    "/{device_id}",
    dependencies=[Depends(require_admin)],
    status_code=204,
    summary="Eliminar un dispositivo",
    description="Permite eliminar dispositivos sin historial de préstamos.",
    response_description="Dispositivo eliminado; respuesta sin cuerpo",
    responses={
        400: {"description": "Restricción de integridad incumplida"},
        404: {"description": "Dispositivo inexistente"},
        409: {"description": "El dispositivo tiene préstamos registrados"}
    }
)
def eliminar_dispositivo(
    device_id: int,
    db: Session = Depends(get_db)
):
    dispositivo = device_services.buscar_dispositivo_por_id(db, device_id)
    device_services.eliminar_dispositivo(db, dispositivo)

    return Response(status_code=204)

@router.get(
    "/{device_id}/loans",
    dependencies=[Depends(require_admin_or_support)],
    response_model=list[LoanDetailResponse],
    summary="Consultar historial de un dispositivo",
    description="Muestra los préstamos del dispositivo y los usuarios asociados.",
    response_description="Historial de préstamos del dispositivo",
    responses={404: {"description": "Dispositivo inexistente"}}
)
def obtener_prestamos_dispositivo(
    device_id: int,
    db: Session = Depends(get_db)
):
    dispositivo = device_services.buscar_dispositivo_por_id(
        db,
        device_id
    )

    return loan_services.listar_prestamos(
        db=db,
        device_id=dispositivo.id
    )