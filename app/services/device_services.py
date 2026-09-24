from fastapi import HTTPException
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Device, Loan
from app.schemas.device_schemas import (
    DeviceCreate,
    DevicePatch,
    DeviceUpdate,
)


def confirmar_cambios(db: Session):
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Los datos incumplen una restricción de integridad."
        )


def buscar_dispositivo_por_id(db: Session, device_id: int) -> Device:
    dispositivo = db.get(Device, device_id)

    if dispositivo is None:
        raise HTTPException(
            status_code=404,
            detail=f"El dispositivo con id {device_id} no fue encontrado"
        )

    return dispositivo


def validar_serie_disponible(
    db: Session,
    serial_number: str,
    device_id: int | None = None
):
    consulta = select(Device).where(
        Device.serial_number == serial_number
    )
    existente = db.scalar(consulta)

    if existente is not None and existente.id != device_id:
        raise HTTPException(
            status_code=400,
            detail="El número de serie ya está registrado"
        )


def listar_dispositivos(
    db: Session,
    device_type: str | None = None,
    is_available: bool | None = None,
    brand: str | None = None,
    search: str | None = None
) -> list[Device]:
    consulta = select(Device)

    if device_type is not None:
        consulta = consulta.where(Device.device_type == device_type)

    if is_available is not None:
        consulta = consulta.where(Device.is_available == is_available)

    if brand is not None:
        consulta = consulta.where(
            func.lower(Device.brand) == brand.lower()
        )

    if search is not None:
        # Tratar %, _ y \ como texto, no como comodines del usuario.
        texto = search.replace("\\", "\\\\")
        texto = texto.replace("%", "\\%").replace("_", "\\_")
        patron = f"%{texto}%"

        consulta = consulta.where(
            or_(
                Device.name.ilike(patron, escape="\\"),
                Device.serial_number.ilike(patron, escape="\\")
            )
        )

    consulta = consulta.order_by(Device.name, Device.id)

    return list(db.scalars(consulta).all())


def registrar_dispositivo(
    db: Session,
    datos: DeviceCreate
) -> Device:
    validar_serie_disponible(db, datos.serial_number)

    dispositivo = Device(**datos.model_dump())

    db.add(dispositivo)
    confirmar_cambios(db)
    db.refresh(dispositivo)

    return dispositivo


def aplicar_cambios(
    db: Session,
    dispositivo: Device,
    cambios: dict
) -> Device:
    if not cambios:
        raise HTTPException(
            status_code=400,
            detail="Debe enviar al menos un campo para actualizar"
        )

    for campo, valor in cambios.items():
        if valor is None and campo != "brand":
            raise HTTPException(
                status_code=422,
                detail=f"El campo {campo} no puede ser null"
            )

    if "serial_number" in cambios:
        validar_serie_disponible(
            db,
            cambios["serial_number"],
            dispositivo.id
        )

    if cambios.get("is_available") is True:
        prestamo_pendiente = db.scalar(
            select(Loan.id).where(
                Loan.device_id == dispositivo.id,
                Loan.return_date.is_(None)
            ).limit(1)
        )

        if prestamo_pendiente is not None:
            raise HTTPException(
                status_code=409,
                detail="El dispositivo tiene un préstamo sin devolver"
            )

    for campo, valor in cambios.items():
        setattr(dispositivo, campo, valor)

    confirmar_cambios(db)
    db.refresh(dispositivo)

    return dispositivo


def actualizar_dispositivo(
    db: Session,
    dispositivo: Device,
    datos: DeviceUpdate
) -> Device:
    return aplicar_cambios(
        db,
        dispositivo,
        datos.model_dump()
    )


def actualizar_dispositivo_parcial(
    db: Session,
    dispositivo: Device,
    datos: DevicePatch
) -> Device:
    return aplicar_cambios(
        db,
        dispositivo,
        datos.model_dump(exclude_unset=True)
    )


def eliminar_dispositivo(db: Session, dispositivo: Device):
    prestamo = db.scalar(
        select(Loan.id).where(
            Loan.device_id == dispositivo.id
        ).limit(1)
    )

    if prestamo is not None:
        raise HTTPException(
            status_code=409,
            detail="No puede eliminar un dispositivo con historial de préstamos"
        )

    db.delete(dispositivo)
    confirmar_cambios(db)