from app.schemas.user_schemas import User

usuarios = [
    User(
        id=1,
        name="Juan Perez",
        email="juan@example.com",
        role="admin",
        is_active=True
    ),
    User(
        id=2,
        name="Maria Lopez",
        email="maria@example.com",
        role="support",
        is_active=True
    ),
    User(
        id=3,
        name="Carlos Sanchez",
        email="carlos@example.com",
        role="user",
        is_active=False
    )
]