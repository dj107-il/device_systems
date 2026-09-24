from datetime import date

from fastapi import APIRouter, Depends, Query
from pydantic import EmailStr
from sqlalchemy.orm import Session

from app.dependencies.database_dependency import get_db
from app.schemas.device_schemas import DeviceType
from app.services import loan_services
from app.schemas.loan_schema import (
    LoanCreate,
    LoanDetailResponse,
    LoanResponse,
    LoanStatus,
)

router = APIRouter(
    prefix="/loans",
    tags=["Loans"]
)

@router.get(
    "",
    response_model=list[LoanResponse],
    summary="Listar y filtrar préstamos",
    description=(
        "Combina filtros por estado, usuario, dispositivo, correo, "
        "tipo, disponibilidad actual y fecha de préstamo."
    ),
    response_description="Préstamos que cumplen los filtros",
    responses={422: {"description": "Filtros inválidos"}}
)
@router.get(
    "/details",
    response_model=list[LoanDetailResponse],
    summary="Consultar préstamos con usuario y dispositivo",
    description=(
        "Consulta mediante joins. Incluye datos relacionados y "
        "permite combinar los mismos filtros del listado."
    ),
    response_description="Préstamos con información relacionada",
    responses={422: {"description": "Filtros inválidos"}}
)
def obtener_prestamos(
    status: LoanStatus | None = None,
    user_id: int | None = Query(default=None, gt=0),
    device_id: int | None = Query(default=None, gt=0),
    user_email: EmailStr | None = None,
    device_type: DeviceType | None = None,
    is_available: bool | None = None,
    fecha_desde: date | None = None,
    fecha_hasta: date | None = None,
    search: str | None = Query(
        default=None,
        min_length=1,
        max_length=100
    ),
    db: Session = Depends(get_db)
):
    return loan_services.listar_prestamos(
        db=db,
        status=status,
        user_id=user_id,
        device_id=device_id,
        user_email=user_email,
        device_type=device_type,
        is_available=is_available,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        search=search
    )
    
@router.get(
    "/{loan_id}",
    response_model=LoanResponse,
    summary="Consultar un préstamo",
    description="Busca un préstamo por su identificador.",
    response_description="Préstamo encontrado",
    responses={
        404: {"description": "Préstamo inexistente"}
    }
)
def obtener_prestamo(
    loan_id: int,
    db: Session = Depends(get_db)
):
    return loan_services.buscar_prestamo_por_id(db, loan_id)

@router.post(
    "",
    response_model=LoanResponse,
    status_code=201,
    summary="Crear un préstamo",
    description=(
        "Asocia un dispositivo disponible a un usuario existente "
        "y marca el dispositivo como no disponible."
    ),
    response_description="Préstamo creado",
    responses={
        404: {"description": "Usuario o dispositivo inexistente"},
        409: {"description": "Dispositivo no disponible o conflicto de integridad"},
        422: {"description": "Datos inválidos"}
    }
)
def crear_prestamo(
    datos: LoanCreate,
    db: Session = Depends(get_db)
):
    return loan_services.registrar_prestamo(db, datos)


@router.patch(
    "/{loan_id}/return",
    response_model=LoanResponse,
    summary="Devolver un dispositivo",
    description=(
        "Registra la devolución del préstamo y vuelve a marcar "
        "el dispositivo como disponible. No requiere cuerpo JSON."
    ),
    response_description="Préstamo devuelto",
    responses={
        404: {"description": "Préstamo inexistente"},
        409: {"description": "El préstamo no admite devolución"}
    }
)
def devolver_prestamo(
    loan_id: int,
    db: Session = Depends(get_db)
):
    return loan_services.devolver_prestamo(db, loan_id)