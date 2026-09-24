from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user_model import User
from app.schemas.user_schemas import UserCreate, UserUpdate, UserPatch
from sqlalchemy import select
from app.models.loan_model import Loan

def buscar_usuario_por_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def buscar_usuario_por_id(db: Session, user_id: int) -> User:
    usuario = db.get(User, user_id)

    if usuario is None:
        raise HTTPException(
            status_code=404,
            detail=f"El usuario con id {user_id} no fue encontrado"
        )

    return usuario

def listar_usuarios(
    db: Session,
    role: str | None = None,
    is_active: bool | None = None,
    ordenar_por: str = "name"
) -> list[User]:
    consulta = db.query(User)

    if role is not None:
        consulta = consulta.filter(User.role == role)

    if is_active is not None:
        consulta = consulta.filter(User.is_active == is_active)

    if ordenar_por == "created_at":
        consulta = consulta.order_by(User.created_at, User.id)
    else:
        consulta = consulta.order_by(User.name, User.id)

    return consulta.all()

def validar_correo_disponible(
    db: Session,
    email: str,
    usuario_id: int | None = None
):
    existente = buscar_usuario_por_email(db, email)

    if existente is not None and existente.id != usuario_id:
        raise HTTPException(
            status_code=400,
            detail=f"El correo electrónico {email} ya está en uso"
        )

def confirmar_cambios(db: Session):
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Los datos incumplen una restricción de la base de datos. \n"
            "Comprueba que el correo no esté registrado."
        )

def registrar_usuario(db: Session, datos: UserCreate) -> User:
    validar_correo_disponible(db, datos.email)

    nuevo_usuario = User(
        name=datos.name,
        email=datos.email,
        role=datos.role,
        is_active=datos.is_active
    )

    db.add(nuevo_usuario)
    confirmar_cambios(db)
    db.refresh(nuevo_usuario)

    return nuevo_usuario

def actualizar_usuario(
    db: Session,
    usuario_actual: User,
    datos: UserUpdate
) -> User:
    validar_correo_disponible(
        db,
        datos.email,
        usuario_actual.id
    )

    usuario_actual.name = datos.name
    usuario_actual.email = datos.email
    usuario_actual.role = datos.role
    usuario_actual.is_active = datos.is_active

    confirmar_cambios(db)
    db.refresh(usuario_actual)

    return usuario_actual

def actualizar_usuario_parcial(
    db: Session,
    usuario_actual: User,
    datos: UserPatch
) -> User:
    cambios = datos.model_dump(exclude_unset=True)

    if not cambios:
        raise HTTPException(
            status_code=400,
            detail="Debe enviar al menos un campo para actualizar"
        )

    # Los campos del usuario no pueden quedar en null
    for campo, valor in cambios.items():
        if valor is None:
            raise HTTPException(
                status_code=422,
                detail=f"El campo {campo} no puede ser null"
            )

    # Se se cambia el correo, comprobar que no perteniezca a otro usuario
    if "email" in cambios:
        validar_correo_disponible(
            db,
            cambios["email"],
            usuario_actual.id
        )

    # Modificar únicamente los campos enviados
    if "name" in cambios:
        usuario_actual.name = cambios["name"]

    if "email" in cambios:
        usuario_actual.email = cambios["email"]

    if "role" in cambios:
        usuario_actual.role = cambios["role"]

    if "is_active" in cambios:
        usuario_actual.is_active = cambios["is_active"]

    confirmar_cambios(db)
    db.refresh(usuario_actual)

    return usuario_actual

def eliminar_usuario(db: Session, usuario_actual: User):
    prestamo = db.scalar(
        select(Loan.id)
        .where(Loan.user_id == usuario_actual.id)
        .limit(1)
    )

    if prestamo is not None:
        raise HTTPException(
            status_code=409,
            detail="No puede eliminar un usuario con historial de préstamos"
        )

    db.delete(usuario_actual)
    confirmar_cambios(db)
