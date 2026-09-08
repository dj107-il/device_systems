from fastapi import FastAPI
from app.routes.user_routes import router as user_router

app = FastAPI(
    title="device_systems",
    version="1.0.0"
)

@app.middleware("http")
async def agregar_cabeceras_personalizadas(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = "1.0"
    return response
    

@app.get("/")
def incio():
    return {
        "message": "API device_systems funcionando correctamente"
    }
    
app.include_router(user_router)