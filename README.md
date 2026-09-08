# device_systems
 
## Descripcion
 
device_systems es una API REST construida con FastAPI que administra el recurso usuarios del sistema. Permite listar usuarios, consultarlos por id, filtrarlos por rol o estado, y registrar usuarios nuevos con validacion de datos mediante Pydantic v2.
 
## Instalacion de dependencias
 
El proyecto usa uv para la gestion de dependencias.
 
```
uv sync
```
 
Si prefieres usar pip con un entorno virtual:
 
```
python -m venv .venv
.venv\Scripts\activate
pip install fastapi uvicorn pydantic email-validator
```
 
## Ejecucion del servidor
 
```
uv run fastapi dev app/main.py
```
 
O con uvicorn directamente:
 
```
uv run uvicorn app.main:app --reload
```
 
El servidor queda disponible en http://127.0.0.1:8000
 
La documentacion interactiva de Swagger UI esta en http://127.0.0.1:8000/docs
 
## Tabla de endpoints
 
| Metodo | Ruta            | Descripcion                                   |
|--------|-----------------|------------------------------------------------|
| GET    | /               | Verifica que la API esta funcionando            |
| GET    | /users          | Lista todos los usuarios                        |
| GET    | /users?role=    | Filtra usuarios por rol (admin, support, user)  |
| GET    | /users?is_active= | Filtra usuarios por estado activo/inactivo    |
| GET    | /users/{user_id} | Consulta un usuario por su id                  |
| POST   | /users          | Registra un nuevo usuario                       |
 
Todas las respuestas incluyen las cabeceras personalizadas X-App-Name y X-API-Version.
 
## Ejemplos de peticiones
 
### GET /users
 
Respuesta:
 
```json
[
  {
    "id": 1,
    "name": "Juan Perez",
    "email": "juan@example.com",
    "role": "admin",
    "is_active": true
  }
]
```
 
### GET /users/1
 
Respuesta:
 
```json
{
  "id": 1,
  "name": "Juan Perez",
  "email": "juan@example.com",
  "role": "admin",
  "is_active": true
}
```
 
### GET /users/99 (usuario inexistente)
 
Respuesta (404):
 
```json
{
  "detail": "Usuario con id 99 no encontrado"
}
```
 
### POST /users
 
Cuerpo de la peticion:
 
```json
{
  "name": "Ana Torres",
  "email": "ana@example.com",
  "role": "user",
  "is_active": true
}
```
 
Respuesta (200):
 
```json
{
  "id": 4,
  "name": "Ana Torres",
  "email": "ana@example.com",
  "role": "user",
  "is_active": true
}
```
 
### POST /users con correo duplicado
 
Respuesta (400):
 
```json
{
  "detail": "El correo electronico ana@example.com ya esta en uso"
}
```
 
## Evidencias de pruebas
 
En esta seccion se deben incluir las capturas de pantalla de:
 
### Swagger UI
- Swagger UI mostrando los endpoints disponibles

![Swagger UI](/images/Swagger_UI_general.png)

### GET /users
- Prueba de GET /users

![GET usuarios](/images/GET_users.png)

### GET /users/{user_id}
- Prueba de GET /users/{user_id}

![GET usuario por id](/images/GET_UserID.png)

### POST /users exitoso
- Prueba de POST /users exitosa

![POST usuario exitoso](/images/POST_exitoso1.png)
![POST usuario exitoso](/images/POST_exitoso2.png)

### POST /users con error de validacion
- Prueba de POST /users con error de validacion (correo duplicado o dato invalido)

![POST error validacion](/images/POST_error_validacion.png)

## Reflexion sobre el uso de FastAPI
 
Desarrollar device_systems me permitió entender de forma práctica cómo FastAPI facilita la
construcción de APIs REST. Organizar el proyecto separando esquemas (schemas) y rutas (routes)
me ayudó a mantener el código ordenado y fácil de escalar si se agregan más recursos además de
usuarios.

El uso de Pydantic v2 fue clave para las validaciones: definir restricciones como el mínimo de
caracteres en el nombre, el formato de correo con EmailStr y los valores permitidos en el rol
con Literal evitó tener que escribir validaciones manuales, y los errores 422 se generan
automáticamente cuando los datos no cumplen el esquema.

Trabajar con Path Parameters y Query Parameters me mostró la diferencia entre identificar un
recurso específico (el id de un usuario) y filtrar una colección (por rol o estado activo).
Finalmente, separar el modelo de entrada (UserCreate) del modelo de respuesta (User) y agregar
cabeceras HTTP personalizadas mediante un middleware me dejó claro por qué es importante
controlar exactamente qué información expone una API hacia el cliente.
 
