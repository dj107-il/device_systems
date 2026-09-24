from fastapi import Depends
from sqlalchemy.orm import Session

from app.dependencies.database_dependency import get_db
from app.models.user_model import User
from app.services.user_services import buscar_usuario_por_id

def obtener_usuario_o_404(
    user_id: int,
    db: Session = Depends(get_db)
) -> User:
    return buscar_usuario_por_id(db, user_id)