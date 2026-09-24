from fastapi import FastAPI, Request

from app.routes.user_routes import router as user_router
from app.routes.device_routes import router as device_router
from app.routes.loan_routes import router as loan_router

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
        },
        {
            "name": "Devices",
            "description": "Gestión de dispositivos tecnológicos."
        },
        {
            "name": "Loans",
            "description": "Préstamos y devoluciones de dispositivos."
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
app.include_router(device_router)
app.include_router(loan_router)