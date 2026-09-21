from app.schemas.user_schemas import User
from app.services.user_services import buscar_usuario_por_id

def obtener_usuario_o_404(user_id: int) -> User:
    return buscar_usuario_por_id(user_id)