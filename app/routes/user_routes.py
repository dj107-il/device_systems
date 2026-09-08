from fastapi import APIRouter, HTTPException
from app.schemas.user_schemas import User, UserCreate
from typing import Optional

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

usuarios = [
    User(
        id=1,
        name = "Juan Pérez",
        email = "juan@example.com",
        role = "admin",
        is_active = True
    ),
    User(
        id=2,
        name = "María López",
        email = "maria@example.com",
        role = "support",
        is_active = True
    ),
    User(
        id=3,
        name = "Carlos García",
        email = "carlos@example.com",
        role = "user",
        is_active = False
    )
]

@router.get("", response_model=list[User])
def obtener_usuarios(
    role: Optional[str] = None,
    is_active: Optional[bool] = None
):
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

@router.get("/{user_id}", response_model=User)
def obtener_usuario(user_id: int):
    for usuario in usuarios:
        if usuario.id == user_id:
            return usuario
        
    raise HTTPException(
        status_code=404,
        detail=f"Usuario con id {user_id} no encontrado"
    )
    
@router.post("/", response_model=User)
def crear_usuario(usuario: UserCreate):
    
    #Verificar si el correo electrónico ya existe
    for usuario_existente in usuarios:
        if usuario_existente.email == usuario.email:
            raise HTTPException(
                status_code=400,
                detail=f"El correo electrónico {usuario.email} ya está en uso"
            )
        
    #Generar un nuevo ID para el usuario
    nuevo_id = max(
        [usuario_existente.id for usuario_existente in usuarios],
        default=0
    ) + 1
    
    #Crear el nuevo usuario
    nuevo_usuario = User(
        id=nuevo_id,
        name=usuario.name,
        email=usuario.email,
        role=usuario.role,
        is_active=usuario.is_active
    )
    
    # Agregar el usuario a la lista
    usuarios.append(nuevo_usuario)
    
    #Retornar el usuario creado 
    return nuevo_usuario