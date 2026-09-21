from typing import Optional 
from fastapi import HTTPException
from app.data.user_db import usuarios
from app.schemas.user_schemas import User, UserCreate, UserUpdate, UserPatch

def listar_usuarios(
    role: Optional[str] = None,
    is_active: Optional[bool] = None
) -> list[User]:
    resultado = usuarios
    
    if role is not None: 
        resultado = [
            usuario for usuario in resultado
            if usuario.role == role
        ]
        
    if is_active is not None:
        resultado = [
            usuario for usuario in resultado
            if usuario.is_active == is_active
        ]
        
    return resultado
    
def buscar_usuario_por_id(user_id: int) -> User:
    for usuario in usuarios:
        if usuario.id == user_id:
            return usuario
        
    raise HTTPException(
        status_code=404,
        detail=f"Usuario con id {user_id} no encontrado"
    )
    
def registrar_usuario(usuario: UserCreate) -> User:
    #Verificación si el correo electrónico ya existe
    for usuario_existente in usuarios:
        if usuario_existente.email == usuario.email:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"El correo electrónico {usuario.email} ya está en uso"
                )
            )
    
    #Generar un nuevo ID
    nuevo_id = max(
        [usuario_existente.id for usuario_existente in usuarios],
        default=0
    ) + 1
    
    # Construir el usuario con los datos recibidos 
    nuevo_usuario = User(
        id=nuevo_id,
        name=usuario.name,
        email=usuario.email,
        role=usuario.role,
        is_active=usuario.is_active 
    )
    
    usuarios.append(nuevo_usuario)
    
    return nuevo_usuario

def actualizar_usuario(
    usuario_actual: User,
    datos: UserUpdate
) -> User:
    #Comprobar si el correo pertenece a otro usuario
    for usuario_existente in usuarios:
        if(
            usuario_existente.email == datos.email
            and usuario_existente.id != usuario_actual.id
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    f"El correo electrónico {datos.email} ya está en uso"
                )
            )
            
    # Actualizar los campos editables del usuario
    usuario_actual.name = datos.name
    usuario_actual.email = datos.email
    usuario_actual.role = datos.role
    usuario_actual.is_active = datos.is_active
    
    return usuario_actual

def actualizar_usuario_parcial(
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
        for usuario_existente in usuarios:
            if(usuario_existente.email == cambios["email"]
               and usuario_existente.id != usuario_actual.id
            ):
                raise HTTPException(
                    status_code=400,
                    detail=f"El correo electrónico {cambios["email"]} ya está en uso."
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
        
    return usuario_actual
            
def eliminar_usuario(usuario_actual: User) -> None:
    usuarios.remove(usuario_actual)
    