from fastapi import FastAPI, Request

from app.database.connection import Base, engine
from app.models.user_model import User
from app.routes.user_routes import router as user_router

# Importar User registra la tabla en los metadatos de Base.
# Crear las tablas que todavia no existan.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="device_systems",
    description="API REST para la gestión de usuarios con persistencia en SQLite mediante SQLAlchemy.",
    version="3.0.0",
    contact={
        "name": "Diego"
    },
    openapi_tags=[
        {
            "name": "Users",
            "description": "Operaciones para gestionar usuarios."
        },
        {
            "name": "Inicio",
            "description": "Comprobación del funcionamiento de la API."
        }
    ]
)

@app.middleware("http")
async def agregar_cabeceras_personalizadas(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = app.version
    return response
    

@app.get(
    "/",
    tags=["inicio"],
    summary="Comprobar el funcionamiento de la API",
    description="Devuelve un mensaje que confirma que la API responde.",
    response_description="Mensaje de funcionamiento"
)
def incio():
    return {
        "message": "API device_systems funcionando correctamente"
    }
    
app.include_router(user_router)