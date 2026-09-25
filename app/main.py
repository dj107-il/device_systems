from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ORIGINS
from app.middlewares.request_middleware import request_middleware
from app.routes.user_routes import router as user_router
from app.routes.device_routes import router as device_router
from app.routes.loan_routes import router as loan_router
from app.auth.auth_routes import router as auth_router
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.rate_limit import limiter

app = FastAPI(
    title="device_systems API",
    description=(
        "API REST segura para gestionar usuarios, dispositivos y préstamos. "
        "Incluye autenticación OAuth2 con JWT, permisos por rol, "
        "persistencia con SQLAlchemy, migraciones Alembic y límites de solicitudes."
    ),    
    version="3.0.0",
    contact={
        "name": "Diego"
    },
    openapi_tags=[
        {
            "name": "Auth",
            "description": "Registro, inicio de sesión y cuenta autenticada."
        },
        {
            "name": "Users",
            "description": "Consulta y administración de usuarios."
        },
        {
            "name": "Devices",
            "description": "Gestión de desipositivos y disponibilidad."
        },
        {
            "name": "Loans",
            "description": "Préstamos, devoluciones, filtros e historiales."
        },
        {
            "name": "Security",
            "description": "Comprobación de la API y cabeceras del middleware."
        }
    ]
)

app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[
        "X-App-Name",
        "X-API-Version",
        "X-Process-Time",
        "X-Request-ID",
    ],
)

app.middleware("http")(request_middleware)

@app.get(
    "/",
    tags=["Security"],
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
app.include_router(auth_router)