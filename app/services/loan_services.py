from datetime import datetime, timezone, date 

from fastapi import HTTPException
from sqlalchemy import and_, func, or_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Device, Loan, User
from app.schemas.loan_schema import LoanCreate

def confirmar_cambios(db: Session):
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="No fue posible guardar el préstamo por una restricción de integridad"
        )


def buscar_prestamo_por_id(db: Session, loan_id: int) -> Loan:
    prestamo = db.get(Loan, loan_id)

    if prestamo is None:
        raise HTTPException(
            status_code=404,
            detail=f"El préstamo con id {loan_id} no fue encontrado"
        )

    return prestamo


def listar_prestamos(
    db: Session,
    status: str | None = None,
    user_id: int | None = None,
    device_id: int | None = None,
    user_email: str | None = None,
    device_type: str | None = None,
    is_available: bool | None = None,
    fecha_desde: date | None = None,
    fecha_hasta: date | None = None,
    search: str | None = None
) -> list[Loan]:
    if (
        fecha_desde is not None
        and fecha_hasta is not None
        and fecha_desde > fecha_hasta
    ):
        raise HTTPException(
            status_code=422,
            detail="fecha_desde no puede ser posterior a fecha_hasta"
        )

    consulta = (
        select(Loan)
        .join(User, Loan.user_id == User.id)
        .join(Device, Loan.device_id == Device.id)
    )

    condiciones = []

    if status is not None:
        condiciones.append(Loan.status == status)

    if user_id is not None:
        condiciones.append(Loan.user_id == user_id)

    if device_id is not None:
        condiciones.append(Loan.device_id == device_id)

    if user_email is not None:
        condiciones.append(
            func.lower(User.email) == user_email.lower()
        )

    if device_type is not None:
        condiciones.append(Device.device_type == device_type)

    if is_available is not None:
        condiciones.append(Device.is_available == is_available)

    if fecha_desde is not None:
        condiciones.append(
            func.date(Loan.loan_date) >= fecha_desde.isoformat()
        )

    if fecha_hasta is not None:
        condiciones.append(
            func.date(Loan.loan_date) <= fecha_hasta.isoformat()
        )

    if search is not None:
        texto = search.replace("\\", "\\\\")
        texto = texto.replace("%", "\\%").replace("_", "\\_")
        patron = f"%{texto}%"

        condiciones.append(
            or_(
                User.name.ilike(patron, escape="\\"),
                User.email.ilike(patron, escape="\\"),
                Device.name.ilike(patron, escape="\\"),
                Device.serial_number.ilike(patron, escape="\\")
            )
        )

    if condiciones:
        consulta = consulta.where(and_(*condiciones))

    consulta = consulta.order_by(
        Loan.loan_date.desc(),
        Loan.id.desc()
    )

    return list(db.scalars(consulta).all())


def registrar_prestamo(db: Session, datos: LoanCreate) -> Loan:
    usuario = db.get(User, datos.user_id)

    if usuario is None:
        raise HTTPException(
            status_code=404,
            detail="El usuario no existe"
        )

    dispositivo = db.get(Device, datos.device_id)

    if dispositivo is None:
        raise HTTPException(
            status_code=404,
            detail="El dispositivo no existe"
        )

    # Reservar el dispositivo solo si continúa disponible.
    resultado = db.execute(
        update(Device)
        .where(
            Device.id == datos.device_id,
            Device.is_available.is_(True)
        )
        .values(is_available=False)
        .execution_options(synchronize_session=False)
    )

    if resultado.rowcount != 1:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="El dispositivo no está disponible"
        )

    prestamo = Loan(
        user_id=datos.user_id,
        device_id=datos.device_id,
        status="active"
    )

    db.add(prestamo)
    confirmar_cambios(db)
    db.refresh(prestamo)

    return prestamo


def devolver_prestamo(db: Session, loan_id: int) -> Loan:
    prestamo = buscar_prestamo_por_id(db, loan_id)

    fecha_devolucion = datetime.now(timezone.utc).replace(tzinfo=None)

    resultado = db.execute(
        update(Loan)
        .where(
            Loan.id == loan_id,
            Loan.return_date.is_(None),
            Loan.status.in_(["active", "overdue"])
        )
        .values(
            status="returned",
            return_date=fecha_devolucion
        )
        .execution_options(synchronize_session=False)
    )

    if resultado.rowcount != 1:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="El préstamo ya fue devuelto o no admite devolución"
        )

    db.execute(
        update(Device)
        .where(Device.id == prestamo.device_id)
        .values(is_available=True)
        .execution_options(synchronize_session=False)
    )

    confirmar_cambios(db)
    db.refresh(prestamo)

    return prestamo