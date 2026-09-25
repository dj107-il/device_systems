# device_systems

## Descripción

**device_systems** es una API REST construida con FastAPI para gestionar usuarios, dispositivos y préstamos. Incluye persistencia con SQLAlchemy y SQLite, migraciones con Alembic, relaciones entre modelos, filtros y validaciones mediante Pydantic v2.

El proyecto evolucionó desde una API básica de usuarios hasta incorporar autenticación OAuth2 con JWT, hash de contraseñas mediante Passlib, permisos por rol, configuración CORS, middleware de trazabilidad y límites de solicitudes.

Las secciones EV08, EV09 y EV10 conservan las evidencias de versiones anteriores. Desde EV11, las operaciones requieren los permisos indicados en la tabla de seguridad.

---

## Tecnologías utilizadas

- Python 3.14 o superior
- FastAPI
- Pydantic v2
- Uvicorn
- uv
- Swagger UI
- ReDoc
- Postman / Thunder Client
- Git y GitHub
- SQLAlchemy 2
- Alembic
- SQLite
- Passlib y bcrypt
- python-jose
- python-multipart
- python-dotenv
- SlowAPI

---

## Estructura del proyecto

```text
device_systems/
├── app/
│   ├── main.py
|   ├── config.py
│   ├── rate_limit.py
│   ├── auth/
│   │   ├── security.py
│   │   ├── auth_service.py
│   │   └── auth_routes.py
│   |
|   ├── middlewares/
│   │   └── request_middleware.py
│   |
│   ├── database/connection.py
|   |
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user_model.py
│   │   ├── device_model.py
│   │   └── loan_model.py
|   |
│   ├── schemas/
│   │   ├── user_schemas.py
│   │   ├── device_schemas.py
│   │   |── loan_schema.py
|   |   └── auth_schema.py
|   |
│   ├── routes/
│   │   ├── user_routes.py
│   │   ├── device_routes.py
│   │   └── loan_routes.py
|   |   
│   ├── services/
│   │   ├── user_services.py
│   │   ├── device_services.py
│   │   └── loan_services.py
|   |
│   └── dependencies/
│       ├── database_dependency.py
│       |── user_dependencies.py
|       └── auth_dependency.py
|
├── images/
│   ├── GA1-EV07/
│   ├── GA1-EV08/
│   ├── GA1-EV09/
│   |── GA1-EV10/
|   └── GA1-EV11/
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── .env.example
├── .env    #Local. No se publica   
├── alembic.ini
├── .gitignore
├── .python-version
├── pyproject.toml
├── requirements.txt
├── uv.lock
└── README.md
```

`device_systems.db` se genera localmente y está excluido de Git, al igual que sus archivos auxiliares, `.venv`, `.env` y la caché de Python.

## Instalación y ejecución

Con Python y uv instalados:

```powershell
git clone https://github.com/dj107-il/device_systems.git
cd device_systems
uv sync --locked
```

En una instalación nueva, copiar la plantilla:

```powershell
Copy-Item .env.example .env
uv run python -c "import secrets; print(secrets.token_hex(32))"
```

Copiar la clave generada en `SECRET_KEY` dentro de `.env`. No sobrescribir un `.env` existente ni publicar su contenido.

```dotenv
SECRET_KEY=REEMPLAZAR_POR_LA_CLAVE_GENERADA
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

Después:

```powershell
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

Una base nueva comienza vacía. Las cuentas con contraseña se crean mediante `POST /auth/register`.

Si se utiliza la alternativa con pip, también se debe configurar `.env` antes de iniciar Uvicorn.

Alternativa con Python 3.14 y pip:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Ejecutar siempre desde la raíz del proyecto. La URL `sqlite:///./device_systems.db` utiliza el directorio de ejecución. Desde EV10, ejecutar `alembic upgrade head` antes de iniciar la aplicación crea o actualiza las tablas. La aplicación ya no ejecuta `Base.metadata.create_all(bind=engine)`. Una instalación nueva comienza sin usuarios; se crean mediante POST.

- [API local](http://127.0.0.1:8000/)
- [Swagger UI](http://127.0.0.1:8000/docs)
- [ReDoc](http://127.0.0.1:8000/redoc)
- [Esquema OpenAPI](http://127.0.0.1:8000/openapi.json)

Para actualizar el archivo de dependencias después de cambios:

```powershell
uv export --format requirements-txt --no-dev --no-hashes --output-file requirements.txt
```

## Modelo de usuario

La respuesta `UserResponse` contiene los siguientes campos. El modelo SQLAlchemy `User` representa su almacenamiento en la tabla `users`:

| Campo | Tipo | Descripción |
|---|---|---|
| `id`        | `int`      | Identificador único del usuario |
| `name`      | `str`      | Nombre del usuario |
| `email`     | `EmailStr` | Correo electrónico válido |
| `role`      | `Literal`  | Rol del usuario |
| `is_active` | `bool`     | Estado activo o inactivo |
| `created_at` | `datetime` | Fecha de creación generada por el servidor |

Los roles permitidos son:

```text
admin
support
user
```

El nombre debe tener entre 3 y 50 caracteres y el correo debe cumplir un formato válido.

---

## Tabla de endpoints

| Metodo | Ruta            | Descripcion                                   |
|--------|-----------------|------------------------------------------------|
| GET    | `/`               | Verifica que la API esta funcionando            |
| GET    | `/users`          | Lista todos los usuarios                        |
| GET    | `/users?role=`    | Filtra usuarios por rol (admin, support, user)  |
| GET    | `/users?is_active=` | Filtra usuarios por estado activo/inactivo    |
| GET    | `/users/{user_id}` | Consulta un usuario por su id                  |
| POST   | `/users/`          | Registra un nuevo usuario                      |
| PUT    | `/users/{user_id}`   | Actualiza completamente un usuario           |
| PATCH  | `/users/{user_id}` | Actualizar parcialmente un usuario             |
| DELETE | `/users/{user_id}` | Elimina un usuario                             |

Las respuestas normales y los errores HTTP controlados incluyen las cabeceras personalizadas `X-App-Name` y `X-API-Version`. EV11 también incorpora `X-Process-Time` y `X-Request-ID`.

```text
X-App-Name: device_systems
X-API-Version: 3.0.0
```

---

## Filtros combinados y ordenamiento (EV09)

Los filtros por `role` e `is_active` pueden combinarse con `ordenar_por`:

```text
GET /users?role=support&is_active=false&ordenar_por=name
GET /users?ordenar_por=created_at
```

`ordenar_por` acepta `name` o `created_at`. El orden es ascendente y, por defecto, se ordena por nombre. El ID es el segundo criterio cuando hay valores iguales. Un valor de ordenamiento inválido devuelve 422; un listado sin coincidencias devuelve `[]` con 200.

## Ejemplos de peticiones

Desde EV11, las peticiones a `/users`, `/devices` y `/loans` requieren un token válido de una cuenta activa. Las operaciones restringidas también requieren el rol correspondiente. Los ejemplos siguientes deben ejecutarse con esos permisos; las capturas de actividades anteriores se conservan como antecedentes.

### GET /users

Respuesta:

```json
[
  {
    "id": 3,
    "name": "Carlos Garcia",
    "email": "carlos@example.com",
    "role": "user",
    "is_active": false,
    "created_at": "2026-09-21T12:00:00"
  },
  {
    "id": 1,
    "name": "Juan Perez",
    "email": "juan@example.com",
    "role": "admin",
    "is_active": true,
    "created_at": "2026-09-21T12:00:00"
  },
  {
    "id": 2,
    "name": "Maria Lopez",
    "email": "maria@example.com",
    "role": "support",
    "is_active": true,
    "created_at": "2026-09-21T12:00:00"
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
  "is_active": true,
  "created_at": "2026-09-21T12:00:00"
}
```

### GET /users/99 (usuario inexistente)

Respuesta (404):

```json
{
  "detail": "El usuario con id 99 no fue encontrado"
}
```

## GET /users?role=admin

Utiliza un **Query Parameter** para filtrar los usuarios por rol.

Ejemplo:

```text
http://127.0.0.1:8000/users?role=admin
```

El resultado contiene únicamente los usuarios cuyo rol sea `admin`.

---

## GET /users?is_active=false

Utiliza un **Query Parameter** para filtrar usuarios según su estado.

Ejemplo:

```text
http://127.0.0.1:8000/users?is_active=false
```

El resultado contiene los usuarios cuyo estado sea `false`.

---

### POST /users/

Desde EV11, esta es una operación administrativa exclusiva del rol `admin`. Crea un usuario sin contraseña habilitada. Para registrar una cuenta con contraseña se utiliza `POST /auth/register`.

### Petición

Cuerpo de la peticion:

```json
{
  "name": "Ana Torres",
  "email": "ana@example.com",
  "role": "user",
  "is_active": true
}
```

### Respuesta

**201 Created**

```json
{
  "id": 4,
  "name": "Ana Torres",
  "email": "ana@example.com",
  "role": "user",
  "is_active": true,
  "created_at": "2026-09-21T12:00:00"
}
```

El sistema valida los datos mediante Pydantic y evita registrar correos electrónicos duplicados.

---

### POST /users/ con correo duplicado

Si se intenta registrar un correo que ya existe:
Respuesta (400):

**400 Bad Request**

```json
{
  "detail": "El correo electrónico ana@example.com ya está en uso"
}
```

## POST /users/ con datos inválidos

Ejemplo:

```json
{
  "name": "Li",
  "email": "correo-invalido",
  "role": "manager",
  "is_active": true
}
```

La API devuelve:

**422 Unprocessable Entity**

Pydantic informa los campos que no cumplen las validaciones establecidas.

---

### PUT /users/{user_id}

El método `PUT` permite actualizar completamente un usuario.

Ejemplo:

```text
PUT /users/4
```

Cuerpo de la peticion:

```json
{
  "name": "Laura Gómez Actualizada",
  "email": "laura@example.com",
  "role": "support",
  "is_active": false
}
```

Respuesta:

**200 OK**

```json
{
  "id": 4,
  "name": "Laura Gómez Actualizada",
  "email": "laura@example.com",
  "role": "support",
  "is_active": false,
  "created_at": "2026-09-21T12:00:00"
}
```

El usuario conserva su ID y su fecha `created_at`; se actualizan los cuatro campos editables.

También se validan situaciones como:

- Correo perteneciente a otro usuario → `400 Bad Request`
- Usuario inexistente → `404 Not Found`
- Información incompleta → `422 Unprocessable Entity`

---

### PATCH /users/{user_id}

El método `PATCH` permite modificar parcialmente un usuario.

Ejemplo:

```text
PATCH /users/4
```

Cuerpo de la peticion:

```json
{
  "role": "admin"
}
```

Respuesta exitosa:

**200 OK**

```json
{
  "id": 4,
  "name": "Laura Gómez Actualizada",
  "email": "laura@example.com",
  "role": "admin",
  "is_active": false,
  "created_at": "2026-09-21T12:00:00"
}
```

Únicamente se modifica el rol, mientras los demás datos permanecen sin cambios.

También se controlan errores como:

- Actualización sin campos → `400 Bad Request`
- Correo duplicado → `400 Bad Request`
- Rol inválido → `422 Unprocessable Entity`
- Valor nulo no permitido → `422 Unprocessable Entity`
- Usuario inexistente → `404 Not Found`

---

### DELETE /users/{user_id}

Permite eliminar un usuario.

Ejemplo:

```text
DELETE /users/4
```

Respuesta:

**204 No Content**

La respuesta exitosa no contiene un cuerpo JSON.

Después de eliminar el usuario, una consulta:

```text
GET /users/4
```

devuelve:

**404 Not Found**

---

# Códigos HTTP utilizados

| Código | Significado | Uso en la API |
|---|---|---|
| `200` | OK | Operaciones GET, PUT y PATCH exitosas |
| `201` | Created | Creación exitosa de usuarios, dispositivos o préstamos |
| `204` | No Content | Eliminación exitosa |
| `400` | Bad Request | Datos o acciones no permitidas |
| `401` | Unauthorized | Token ausente, inválido o vencido; credenciales incorrectas |
| `403` | Forbidden | Cuenta inactiva o rol sin permisos |
| `404` | Not Found | Recurso inexistente |
| `409` | Conflict | Conflicto de negocio, como dispositivo ocupado o recurso con historial |
| `422` | Unprocessable Entity | Datos que no cumplen las validaciones |
| `429` | Too Many Requests | Límite de solicitudes excedido |

---

# Validaciones con Pydantic

Pydantic permite validar automáticamente los datos recibidos por la API.

Entre las validaciones implementadas se encuentran:

- Nombre obligatorio.
- Nombre con entre 3 y 50 caracteres.
- Correo electrónico con formato válido.
- Roles limitados a `admin`, `support` y `user`.
- Estado del usuario como valor booleano.
- Rechazo de datos que no cumplen el esquema.

Esto permite que FastAPI genere respuestas `422` cuando los datos enviados no cumplen las reglas definidas.

---

# Parámetros de ruta y consulta

La API utiliza diferentes tipos de parámetros.

### Path Parameter

Se utiliza para identificar un recurso específico:

```text
GET /users/{user_id}
```

Ejemplo:

```text
GET /users/1
```

El valor `1` corresponde al identificador del usuario.

### Query Parameter

Se utiliza para filtrar la colección:

```text
GET /users?role=admin
```

o:

```text
GET /users?is_active=true
```

Esto permite consultar usuarios según diferentes criterios sin modificar la ruta principal del recurso.

---

# Response Models

La aplicación utiliza modelos de respuesta para establecer la estructura de los datos que devuelve la API.

Esto permite:

- Estandarizar las respuestas.
- Validar la información enviada al cliente.
- Controlar qué información expone la API.
- Mantener una estructura consistente en los endpoints.

---

# Cabeceras HTTP personalizadas

La API incorpora cabeceras HTTP personalizadas para identificar la aplicación y la versión de la API:

```text
X-App-Name: device_systems
X-API-Version: 3.0.0
```

Estas cabeceras pueden ser consultadas desde Swagger, Postman o cualquier otro cliente HTTP.

---

## Evidencias de pruebas de EV08

Estas capturas se conservan como antecedentes de la actividad anterior. Las evidencias de la versión con SQLite se encuentran en la sección **Evidencias EV09**.

### Swagger UI

- Swagger UI mostrando los endpoints disponibles

![Swagger UI](images/GA1-EV08/ev08_swagger.png)

---

### GET /users

- Consulta de todos los usuarios:

![GET usuarios](images/GA1-EV08/ev08_get_usuarios.png)

### GET /users/{user_id}

- Consulta de un usuario mediante Path Parameter:

![GET usuario por id](images/GA1-EV08/ev08_get_usuario.png)

## GET /users?role=admin

Filtro de usuarios mediante Query Parameter:

![Filtro por rol](images/GA1-EV08/ev08_filtro_rol.png)

---

## GET /users?is_active=false

Filtro de usuarios por estado:

![Filtro por estado](images/GA1-EV08/ev08_filtro_estado.png)

---

## GET /users/999

Prueba de usuario inexistente:

![GET 404](images/GA1-EV08/ev08_get_404.png)

---

### POST /users/ exitoso

- Registro exitoso de un nuevo usuario:

![POST usuario exitoso](images/GA1-EV08/ev08_post_201.png)

### POST /users/ con error de validacion

- Prueba de POST /users/ con error de validacion (correo duplicado o dato invalido)

![POST correo duplicado](images/GA1-EV08/ev08_post_400.png)
![POST datos invalidos](images/GA1-EV08/ev08_post_422.png)

---

## PUT /users/{user_id}

Actualización completa de un usuario:

![PUT exitoso](images/GA1-EV08/ev08_put_200.png)

---

## PATCH /users/{user_id}

Actualización parcial de un usuario:

![PATCH exitoso](images/GA1-EV08/ev08_patch_200.png)

---

## DELETE /users/{user_id}

Eliminación de un usuario:

![DELETE exitoso](images/GA1-EV08/ev08_delete_204.png)

---

## ReDoc

Documentación de la API mediante ReDoc:

![ReDoc](images/GA1-EV08/ev08_redoc1.png)

![ReDoc](images/GA1-EV08/ev08_redoc2.png)

---

# Pruebas con cliente HTTP externo

Además de Swagger UI, la API puede ser probada mediante herramientas como **Postman** o **Thunder Client**.

La dirección base utilizada es:

```text
http://127.0.0.1:8000
```

Las pruebas principales incluyen:

1. Consulta de usuarios mediante GET.
2. Consulta de usuario por ID.
3. Registro mediante POST.
4. Actualización completa mediante PUT.
5. Actualización parcial mediante PATCH.
6. Eliminación mediante DELETE.

Estas pruebas permiten comprobar el comportamiento de la API desde un cliente externo a Swagger.

**Evidencias anteriores de EV08 (con Postman):**

![Postman GET /users](images/GA1-EV08/ev08_get_users_postman.png)

![Postman GET /users/{user_id}](images/GA1-EV08/ev08_users_id_postman.png)

![Postman PATCH error de correo duplicado](images/GA1-EV08/ev08_correo_duplicado_400_postman.png)

![Postman DELETE /users/{user_id}](images/GA1-EV08/ev08_delete_404_postman.png)

---

# Dependency Injection

En el proyecto se aplicó **Dependency Injection (DI)** mediante la función `Depends()` proporcionada por FastAPI.

Se creó una dependencia llamada `obtener_usuario_o_404` en el módulo `app/dependencies/user_dependencies.py`. En EV09, `User` se importa desde `app.models.user_model`, `Session` desde `sqlalchemy.orm` y `get_db` desde la dependencia de base de datos. Esta función recibe el `user_id` y una sesión, busca el usuario mediante la capa de servicios y devuelve el usuario encontrado. Si el usuario no existe, se genera una respuesta `404 Not Found`.

```python
def obtener_usuario_o_404(
    user_id: int,
    db: Session = Depends(get_db)
) -> User:
    return buscar_usuario_por_id(db, user_id)
```

Esta dependencia se utiliza en los endpoints que necesitan obtener un usuario específico. Mediante Depends(), FastAPI se encarga de ejecutar la dependencia y proporcionar el resultado directamente al endpoint.

Por ejemplo:

```python
usuario: User = Depends(obtener_usuario_o_404)
```

De esta manera, la lógica para buscar un usuario y controlar su existencia no necesita repetirse en cada endpoint. Esto permite separar responsabilidades, reducir código repetido y facilitar el mantenimiento del proyecto.

## Modelo SQLAlchemy y schemas Pydantic

| Elemento | Responsabilidad |
|---|---|
| `User` en `models/user_model.py` | Representa la tabla `users` y sus restricciones |
| `UserCreate` | Valida la creación; `is_active` vale `True` si se omite |
| `UserUpdate` | Exige los cuatro campos editables para PUT |
| `UserPatch` | Permite omitir campos para PATCH |
| `UserResponse` | Define la salida con ID y fecha de creación |

`ConfigDict(from_attributes=True)` permite a `UserResponse` leer los atributos de los objetos SQLAlchemy. Los schemas no son tablas ni guardan datos por sí mismos.

### Tabla users y restricciones

| Columna | Tipo SQLAlchemy | Regla |
|---|---|---|
| `id` | Integer | Clave primaria generada por SQLite |
| `name` | String(50) | No admite NULL |
| `email` | String(255) | Único, obligatorio e indexado |
| `role` | String(20) | No admite NULL |
| `is_active` | Boolean | No admite NULL; valor predeterminado de SQLAlchemy: True |
| `created_at` | DateTime | No admite NULL; fecha generada al insertar |
| `hashed_password` | String(255) | Incorporado en EV11. No admite NULL; almacena el hash o la marca `"!"` para cuentas sin contraseña habilitada. Se excluye de las respuestas. |

Las fechas se guardan en UTC sin información de zona horaria en SQLite. El cliente no proporciona el ID ni la fecha; PUT y PATCH los conservan.

Pydantic valida nombres de 3 a 50 caracteres, formato de correo y roles `admin`, `support` o `user`. La base de datos aplica la unicidad y la obligatoriedad. SQLite no impone por sí solo la longitud declarada en `String(50)`; esa validación se realiza en la entrada de la API. Los roles permitidos se validan en Pydantic, no mediante un CHECK en la tabla.

## Sesiones, dependencias y transacciones

`connection.py` define el motor `engine`, la fábrica de sesiones `SessionLocal` y la base declarativa `Base`.

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

`Depends(get_db)` proporciona una sesión por petición y garantiza su cierre. La dependencia `obtener_usuario_o_404` utiliza esa sesión para consultar el ID y devolver 404 si no existe. FastAPI reutiliza la dependencia de sesión dentro de la misma petición por defecto.

Los servicios ejecutan consultas y operaciones. `add()` prepara una inserción, `commit()` confirma los cambios, `refresh()` recupera valores guardados y `delete()` prepara una eliminación. Si ocurre un `IntegrityError`, se ejecuta `rollback()` y se devuelve 400. Antes de guardar se comprueba también que el correo no pertenezca a otro usuario.

## Persistencia y comprobaciones

Para comprobar la persistencia: crear un usuario, anotar su ID, detener el servidor, iniciarlo desde la misma carpeta y consultar el ID. El registro debe permanecer. Las actualizaciones y eliminaciones también se confirman en SQLite.

La persistencia tras reinicio fue comprobada durante el desarrollo. Para repetir las pruebas funcionales desde Swagger, Postman o Thunder Client:

1. Crear un usuario válido: 201; repetir el correo: 400.
2. Listar y consultar el ID: 200; consultar un ID inexistente: 404.
3. Filtrar por rol y estado; comprobar orden por nombre y fecha.
4. Ejecutar PUT completo y PATCH parcial: 200; verificar con GET.
5. Enviar datos inválidos: 422; PATCH vacío: 400.
6. Eliminar: 204; consultar y eliminar nuevamente: 404.

`create_all()` crea tablas inexistentes; no migra la estructura de tablas existentes. Esta versión es una aplicación de formación con SQLite local y no incorpora autenticación.

## Evidencias EV09

### Estructura y base de datos

![Estructura del proyecto](images/GA1-EV09/ev09_estructura.png)
![Base de datos generada](images/GA1-EV09/ev09_base_datos.png)

### Swagger UI

![Swagger EV09](images/GA1-EV09/ev09_swagger.png)

### Consulta de usuarios: GET

![Listado de usuarios con respuesta 200](images/GA1-EV09/ev09_get_usuarios.png)

![Consulta por ID con respuesta 200](images/GA1-EV09/ev09_get_usuario.png)

### Creación: POST

![POST: petición](images/GA1-EV09/ev09_POST_201_parte1.png)
![POST: respuesta](images/GA1-EV09/ev09_POST_201_parte2.png)

### Actualización completa: PUT

![PUT exitoso](images/GA1-EV09/ev09_PUT_200.png)

### Actualización parcial: PATCH

![PATCH exitoso](images/GA1-EV09/ev09_PATCH_200.png)

### Eliminación: DELETE

![DELETE exitoso](images/GA1-EV09/ev09_DELETE_204.png)

### Errores controlados

![Correo duplicado](images/GA1-EV09/ev09_correo_duplicado_400.png)
![Datos inválidos](images/GA1-EV09/ev09_validacion_422.png)
![Usuario inexistente](images/GA1-EV09/ev09_usuario_404.png)

# Reflexión final sobre la evolución del proyecto

El proyecto `device_systems` evolucionó progresivamente desde una API básica hasta una aplicación backend con una estructura más organizada y funcionalidades orientadas a un escenario real de gestión de usuarios.

Inicialmente se trabajó con la configuración básica de FastAPI y la creación de los primeros endpoints. Posteriormente se incorporaron modelos con Pydantic v2 para validar la información recibida, parámetros de ruta y consulta para realizar búsquedas y filtros, y diferentes métodos HTTP para gestionar las operaciones sobre los usuarios.

A medida que avanzó el proyecto también se implementaron Response Models, manejo estructurado de errores, códigos de estado HTTP, cabeceras personalizadas y Dependency Injection mediante `Depends()`. Esto permitió comprender que una API no consiste únicamente en crear endpoints, sino también en organizar correctamente sus responsabilidades y controlar la información que recibe y devuelve.

Finalmente, las pruebas realizadas mediante Swagger UI y clientes HTTP permitieron comprobar tanto los casos exitosos como los diferentes escenarios de error. Esta evolución permitió pasar de una implementación funcional básica a una API REST más estructurada, validada, documentada y preparada para futuras ampliaciones.

# Reflexión sobre el uso de FastAPI

Desarrollar `device_systems` me permitió entender de forma práctica cómo FastAPI facilita la construcción de APIs REST. Organizar el proyecto separando esquemas (`schemas`), rutas (`routes`), servicios (`services`), modelos (`models`), conexión a la base de datos (`database`) y dependencias (`dependencies`) me ayudó a mantener el código ordenado y fácil de escalar si se agregan más recursos además de usuarios.

El uso de Pydantic v2 fue clave para las validaciones: definir restricciones como el mínimo de caracteres en el nombre, el formato de correo con `EmailStr` y los valores permitidos en el rol con `Literal` evitó tener que escribir validaciones manuales. Además, los errores `422` se generan automáticamente cuando los datos recibidos no cumplen con el esquema definido.

Trabajar con Path Parameters y Query Parameters me permitió comprender la diferencia entre identificar un recurso específico mediante su ID y filtrar una colección de usuarios mediante criterios como el rol o el estado activo.

Finalmente, separar el modelo de entrada (`UserCreate`) del schema de respuesta (`UserResponse`), implementar Response Models, manejar errores HTTP y utilizar cabeceras HTTP personalizadas mediante middleware permitió comprender la importancia de controlar exactamente qué información recibe y expone una API hacia el cliente.

## Reflexión final sobre la importancia de la persistencia (EV09)

La evolución a SQLite permitió comprender que conservar datos requiere confirmar operaciones en una base de datos. Reiniciar el servidor ya no elimina los usuarios registrados. Separar el modelo SQLAlchemy de los schemas Pydantic ayudó a distinguir el almacenamiento de la validación y de las respuestas HTTP.

Las sesiones y las transacciones permiten agrupar y confirmar cambios; el rollback recupera la sesión cuando falla una restricción. La validación de entrada y las restricciones de la tabla se complementan: Pydantic comprueba el contenido recibido y SQLite protege reglas como la unicidad del correo. La organización en rutas, servicios, modelos y dependencias permitió evolucionar el proyecto conservando sus operaciones REST.

# Conclusión

El proyecto `device_systems` cumple con la implementación de una API REST para la gestión de usuarios, incluyendo:

- Endpoints GET.
- Path Parameters.
- Query Parameters.
- Endpoint POST.
- Validaciones con Pydantic v2.
- Response Models.
- Métodos PUT y PATCH.
- Eliminación mediante DELETE.
- Manejo de errores HTTP.
- Dependency Injection mediante Depends().
- Cabeceras HTTP personalizadas.
- Documentación mediante Swagger UI y ReDoc.
- Pruebas funcionales de los diferentes escenarios.
- Organización modular mediante rutas, esquemas, servicios, modelos, conexión a la base de datos y dependencias.
- Persistencia con SQLAlchemy y SQLite.
- Fecha de creación y ordenamiento de usuarios.
- Sesiones y manejo de restricciones de integridad.

## Control de versiones

EV09 se desarrolla en `feature/fastapi-sqlalchemy-ev09`. Tras revisar y probar los cambios, se integra en `develop`; la versión de entrega se publica en `main`. El historial conserva el desarrollo de las actividades anteriores.


## EV10 — Migraciones, relaciones y consultas avanzadas

La actividad GA1-220501096-01-AA1-EV10 amplía usuarios con dispositivos y préstamos. Se conserva la documentación de EV08 y EV09 como antecedente y se añaden estas instrucciones para la versión actual.

### Estado de la revisión local del 24 de septiembre de 2026

Se ejecutaron 50 comprobaciones HTTP sobre una base de pruebas independiente: **49 aprobadas y 1 fallida en la primera ejecución**. La base original no fue utilizada para estas operaciones. No se realizaron commits ni publicaciones durante esta revisión.

**Corrección verificada:** el aprendiz restauró `GET /loans/{loan_id}`. La comprobación posterior confirmó 200 para el préstamo existente, 404 para uno inexistente, 200 para `/loans/details` y el registro en OpenAPI. Las 50 comprobaciones originales quedan cubiertas entre la ejecución inicial y esta repetición dirigida; no se repitió toda la batería.

### Migraciones con Alembic

Para ejecutar la versión actual del proyecto, primero se debe configurar `.env` siguiendo la sección «Instalación y ejecución» del inicio del README. Después se aplican las migraciones y se inicia la API.

```powershell
uv sync --locked
uv run alembic upgrade head
uv run alembic current
uv run alembic check
uv run uvicorn app.main:app --reload
```

Las migraciones versionan los cambios estructurales. `upgrade head` aplica las pendientes, `current` muestra la revisión de la base, `history` lista la secuencia y `check` compara la estructura con los modelos.

| Revisión | Cambio |
|---|---|
| `1c71b07f1dad` | Crea users y el índice único del correo |
| `4ed025fa5b12` | Crea devices y loans con índices y claves foráneas |

```powershell
uv run alembic history
```

Durante la configuración inicial se utilizó `uv run alembic init alembic`. No se repite sobre una carpeta ya inicializada. Para nuevos cambios de modelos se genera una revisión con `uv run alembic revision --autogenerate -m "descripcion del cambio"`, se revisa el archivo y luego se aplica.

Para incorporar la base de EV09 ya existente se verificó previamente que su tabla users coincidiera con la revisión inicial. Solo en ese caso se registró esa revisión mediante `stamp 1c71b07f1dad`; luego se aplicó la segunda migración. **Una instalación vacía usa upgrade, no stamp.**

Ante un fallo: detener la actualización, leer el error, comprobar URL y revisión, revisar la migración y respaldar los datos antes de corregir. SQLite puede dejar cambios DDL parciales; no asumir que todo se deshizo. No usar `stamp head` para ocultar un error ni borrar la base original. La configuración y las revisiones se guardan en Git; los archivos .db permanecen excluidos.

### Relaciones y reglas

```text
User 1 ─── N Loan N ─── 1 Device
```

`ForeignKey` vincula cada préstamo con usuarios y dispositivos existentes. `relationship` y `back_populates` permiten recorrer ambas direcciones desde Python. El motor de la aplicación activa `PRAGMA foreign_keys=ON` en cada conexión SQLite.

- Device tiene serie única, nombre, tipo, marca opcional, disponibilidad y fecha de creación.
- Loan guarda usuario, dispositivo, fecha de préstamo, fecha de devolución opcional y estado.
- Crear un préstamo reserva el dispositivo y guarda ambas operaciones en una transacción.
- Devolverlo registra la fecha, establece returned y libera el dispositivo.
- No se permite volver a prestar un dispositivo ocupado ni devolver dos veces un préstamo: 409.
- Usuarios y dispositivos con historial no pueden eliminarse: 409, aunque todos sus préstamos estén devueltos.
- Los schemas validan la entrada; la base aplica restricciones. El estado overdue se admite, pero no se calcula automáticamente porque no existe fecha límite de devolución.

### Endpoints de EV10

| Método y ruta | Operación |
|---|---|
| GET /devices | Listar y filtrar dispositivos |
| GET /devices/{device_id} | Consultar dispositivo |
| POST /devices | Crear: 201 |
| PUT /devices/{device_id} | Actualizar todos los campos editables |
| PATCH /devices/{device_id} | Actualización parcial; solo brand admite null |
| DELETE /devices/{device_id} | Eliminar sin historial: 204 sin cuerpo |
| GET /loans | Listar y filtrar préstamos |
| GET /loans/details | Préstamos con usuario y dispositivo |
| GET /loans/{loan_id} | Consultar préstamo por ID: 200; inexistente: 404 |
| POST /loans | Crear préstamo: 201 |
| PATCH /loans/{loan_id}/return | Devolver: 200; no requiere JSON |
| GET /users/{user_id}/loans | Historial del usuario |
| GET /devices/{device_id}/loans | Historial del dispositivo |

Las consultas exitosas devuelven 200. Los recursos inexistentes devuelven 404, las series duplicadas 400, los conflictos de negocio 409 y los datos o filtros inválidos 422.

### Joins y filtros

`select(Loan).join(User).join(Device)` representa la combinación de tablas; el servicio concreta las condiciones mediante sus claves. `where` añade filtros, `and_` combina los filtros enviados y `or_` permite buscar en varios campos con `ilike`.

```text
GET /devices?device_type=laptop&brand=lenovo&is_available=true
GET /devices?search=thinkpad
GET /loans/details
GET /loans?status=returned&device_type=laptop
GET /loans?user_email=aprendiz.ev10@example.com
GET /loans?user_id=1&device_id=1
GET /loans/details?search=ThinkPad
GET /loans?fecha_desde=2026-09-24&fecha_hasta=2026-09-24
```

Las fechas se refieren al día UTC de creación del préstamo, incluyen ambos extremos y usan YYYY-MM-DD. Un intervalo invertido devuelve 422. `is_available` filtra la disponibilidad actual del dispositivo. Un filtro sin coincidencias devuelve una lista vacía con 200.

### Evidencias de EV10

Estas evidencias se conservan como registro de las pruebas de EV10. Las pruebas de autenticación, permisos y protección incorporadas posteriormente se encuentran en la sección EV11.

### Consultas relacionadas y filtros

![Consulta de préstamo por ID](images/GA1-EV10/ev10_prestamo_id_200.png)
![Préstamo inexistente](images/GA1-EV10/ev10_prestamo_id_404.png)
![Consulta con joins](images/GA1-EV10/ev10_joins_200.png)
![Filtros combinados](images/GA1-EV10/ev10_filtros_combinados.png)
![Búsqueda por texto](images/GA1-EV10/ev10_busqueda_200.png)
![Filtro por fecha](images/GA1-EV10/ev10_filtro_fecha_200.png)
![Fechas inválidas](images/GA1-EV10/ev10_fechas_invalidas_422.png)

### Historiales

![Historial del usuario](images/GA1-EV10/ev10_historial_usuario_200.png)
![Historial del dispositivo](images/GA1-EV10/ev10_historial_dispositivo_200.png)

### Actualización, eliminación e integridad

![Actualización completa](images/GA1-EV10/ev10_put_device_200.png)
![Eliminación exitosa](images/GA1-EV10/ev10_delete_device_204.png)
![Consulta después de eliminar](images/GA1-EV10/ev10_device_eliminado_404.png)
![Protección del usuario con historial](images/GA1-EV10/ev10_delete_usuario_historial_409.png)
![Protección del dispositivo con historial](images/GA1-EV10/ev10_delete_dispositivo_historial_409.png)

### Usuario, documentación y migraciones

![Creación de dispositivo](images/GA1-EV10/ev10_post_201.png)
![Swagger actualizado](images/GA1-EV10/ev10_swagger_final_revision.png)
![Verificación de migraciones](images/GA1-EV10/ev10_alembic_verificacion.png)
![Estructura de tablas, parte ](images/GA1-EV10/ev10_tabla_estructura.png)

### Reflexión sobre migraciones, relaciones y consultas

Las migraciones permiten describir cómo evoluciona la base de datos y reproducir su estructura en otra instalación. Las relaciones permiten conservar el historial de préstamos sin repetir todos los datos del usuario o del dispositivo. Las claves foráneas y las transacciones ayudan a evitar registros huérfanos y cambios incompletos. Los joins y los filtros convierten esos datos relacionados en consultas útiles, como conocer quién recibió un equipo y cuándo lo devolvió.

## EV11 — Seguridad, autenticación y protección de la API

La actividad GA1-220501096-01-AA1-EV11 incorpora seguridad sobre la funcionalidad de usuarios, dispositivos y préstamos desarrollada en las actividades anteriores.

### Funcionalidades incorporadas

- Registro de cuentas con contraseña.
- Hash de contraseñas mediante Passlib y bcrypt.
- Login mediante formulario OAuth2.
- Tokens JWT con vencimiento.
- Consulta de la cuenta autenticada mediante `/auth/me`.
- Protección de rutas y autorización por roles.
- Validación de contraseñas con Pydantic v2.
- Configuración de orígenes permitidos mediante CORS.
- Middleware con tiempo de procesamiento e identificador de petición.
- Límites de solicitudes mediante SlowAPI.

### Migración de autenticación

La revisión `52931945d101`, posterior a `4ed025fa5b12`, incorpora `hashed_password` a la tabla `users`.

El campo no admite NULL y no se incluye en `UserResponse`. Los usuarios anteriores conservan sus datos e historial, pero reciben la marca `"!"`, que representa una contraseña no habilitada. Esa marca no permite iniciar sesión.

Las nuevas cuentas creadas mediante `/auth/register` almacenan un hash real. No se asignó una contraseña común a los usuarios anteriores.

```powershell
uv run alembic current
uv run alembic check
uv run alembic history
```

![Migración de autenticación aplicada](images/GA1-EV11/ev11_alembic_verificacion.png)

### Registro y validación

`POST /auth/register` recibe nombre, correo, contraseña y rol `user`.

La contraseña debe cumplir:

- Mínimo ocho caracteres.
- Al menos una mayúscula.
- Al menos una minúscula.
- Al menos un número.
- Sin espacios en blanco.
- Máximo 72 bytes al codificarse en UTF-8, por el límite de bcrypt.
- Sin caracteres nulos.

El registro público rechaza los roles `admin` y `support`, así como campos adicionales no definidos en el schema.

Ejemplo con datos exclusivamente de prueba:

```json
{
  "name": "Laura Seguridad",
  "email": "laura.ev11@example.com",
  "password": "PruebaSegura2026",
  "role": "user"
}
```

Una creación correcta devuelve 201. Un correo duplicado devuelve 400 y los datos inválidos devuelven 422.

`SecretStr` oculta la contraseña en la representación del objeto. El servicio obtiene su valor para generar el hash; no guarda el texto original.

### Hash y autenticación

El hash no es un cifrado reversible. `get_password_hash()` genera el valor que se almacena y `verify_password()` comprueba una contraseña contra ese valor.

`POST /auth/login` recibe un formulario:

- `username`: correo de la cuenta.
- `password`: contraseña.

Una autenticación correcta devuelve:

```json
{
  "access_token": "<token generado>",
  "token_type": "bearer"
}
```

La contraseña incorrecta produce 401. Una cuenta con credenciales correctas pero inactiva produce 403.

El token contiene el identificador del usuario en `sub`, el momento de emisión en `iat` y el vencimiento en `exp`. Se firma con HS256 y una clave configurada en `.env`. No contiene contraseñas ni hashes.

Las peticiones protegidas envían:

```http
Authorization: Bearer <token>
```

Las dependencias validan el token y consultan al usuario en SQLite para comprobar su existencia, estado y rol.

### Uso desde Swagger

1. Registrar una cuenta mediante `/auth/register`.
2. Pulsar **Authorize**.
3. Introducir el correo en `username` y la contraseña en `password`.
4. Autorizar y ejecutar `/auth/me`.
5. Cerrar la sesión mediante **Logout** para probar otra cuenta.

Ejecutar `/auth/login` manualmente devuelve el token, pero no autoriza automáticamente las demás peticiones de Swagger.

### Roles y permisos

Todas las rutas de `/users`, `/devices` y `/loans` requieren una cuenta autenticada y activa.

| Operación | Permiso |
|---|---|
| GET `/users` y GET `/users/{user_id}` | Cuenta autenticada y activa |
| POST, PUT, PATCH y DELETE de usuarios | Admin |
| GET de dispositivos, listado y por ID | Cuenta autenticada y activa |
| POST, PUT y PATCH de dispositivos     | Admin o support |
| DELETE de dispositivos                | Admin |
| GET `/loans` y GET `/loans/{loan_id}` | Cuenta autenticada y activa |
| POST `/loans`                         | Cuenta autenticada y activa |
| GET `/loans/details`                  | Admin o support |
| PATCH `/loans/{loan_id}/return`       | Admin o support |
| Historiales de usuarios y dispositivos| Admin o support |

La autorización implementada es por rol. En esta versión, las consultas generales de préstamos no se restringen automáticamente a los préstamos propios.

Los permisos no reemplazan las reglas de integridad: un administrador tampoco puede eliminar un dispositivo con historial de préstamos.

### Primer administrador

El registro público siempre crea cuentas con rol `user`.

Para preparar las cuentas de prueba se registraron cuentas normales y se asignaron los roles desde una sesión local controlada de SQLAlchemy. No existe un endpoint público para convertirse en administrador.

Ejemplo de asignación inicial, después de registrar la cuenta indicada:

```powershell
@'
from sqlalchemy import select
from app.database.connection import SessionLocal
from app.models.user_model import User

with SessionLocal() as db:
    usuario = db.scalar(
        select(User).where(User.email == "admin.ev11@example.com")
    )

    if usuario is None:
        raise SystemExit("Primero registra la cuenta.")

    if not usuario.is_active or usuario.hashed_password == "!":
        raise SystemExit("La cuenta debe estar activa y tener contraseña.")

    usuario.role = "admin"
    db.commit()

print("Rol administrador asignado.")
'@ | uv run python -
```

Las cuentas antiguas sin contraseña habilitada necesitan un procedimiento de asignación antes de poder iniciar sesión. No se ha implementado recuperación de contraseña.

### CORS

Los orígenes permitidos se configuran mediante `CORS_ORIGINS`:

```dotenv
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

La configuración habilita credenciales y expone las cabeceras personalizadas al frontend.

Se utilizan orígenes concretos en lugar de `"*"` porque el acceso con credenciales requiere controlar explícitamente los orígenes autorizados.

CORS es una política aplicada por los navegadores. No reemplaza la autenticación ni impide por sí mismo que herramientas como curl envíen peticiones.

Se comprobó una petición previa OPTIONS:

- Origen permitido: 200 con `Access-Control-Allow-Origin`.
- Origen no permitido: 400, sin autorizar ese origen.

### Middleware de trazabilidad

El middleware agrega:

| Cabecera | Contenido |
|---|---|
| `X-App-Name`    | `device_systems` |
| `X-API-Version` | Versión de la API |
| `X-Process-Time`| Tiempo de procesamiento en segundos |
| `X-Request-ID`  | Identificador de la petición |

Si llega un `X-Request-ID` con formato permitido, se conserva. En otro caso se genera uno nuevo.

Los registros incluyen método, ruta, estado, identificador y tiempo. No se registran cuerpos de petición ni cabeceras de autorización.

Las respuestas normales y los errores HTTP controlados reciben las cabeceras. Una excepción no controlada se registra y vuelve a propagarse; este middleware no garantiza esas cabeceras en la respuesta 500 generada por el servidor.

### Límites de solicitudes

SlowAPI aplica límites por dirección IP y endpoint:

| Endpoint | Límite |
|---|---|
| POST `/auth/login`    | 5 por minuto |
| POST `/auth/register` | 3 por minuto |
| GET `/users`          | 30 por minuto |
| POST `/loans`         | 10 por minuto |

Al exceder el límite se responde 429.

Los contadores se almacenan en memoria, se reinician al reiniciar el proceso y no se comparten entre varios procesos. Es una configuración para el entorno local de esta actividad.

Las solicitudes que llegan al controlador también cuentan cuando fallan por credenciales incorrectas, correo duplicado o recurso inexistente. Las solicitudes rechazadas antes, por validación o dependencias, pueden no llegar al contador del decorador.

Se comprobó el límite de login: cinco intentos con contraseña incorrecta devolvieron 401 y el sexto devolvió 429. Después de terminar la ventana, una nueva petición volvió a responder 401.

También se comprobaron los otros tres límites:

| Endpoint | Respuestas antes del límite | Respuesta al excederlo |
|---|---|---|
| POST `/auth/register` | Tres respuestas 400 por correo duplicado | Cuarta solicitud: 429 |
| GET `/users`          | Treinta respuestas 200 | Solicitud 31: 429 |
| POST `/loans`         | Diez respuestas 404 por usuario inexistente | Solicitud 11: 429 |

Estas pruebas no crearon nuevos usuarios ni préstamos.

![Límite de registro](images/GA1-EV11/ev11_rate_limit_register_429.png)

![Límite de consulta de usuarios](images/GA1-EV11/ev11_rate_limit_users_429.png)

![Límite de creación de préstamos](images/GA1-EV11/ev11_rate_limit_loans_429.png)

### Estructura del proyecto en EV11

![Estructura del proyecto](images/GA1-EV11/ev11_estructura.png)

### Evidencias de autenticación

La captura de registro muestra 201, aunque su nombre de archivo conserva “200”.

![Registro correcto](images/GA1-EV11/ev11_POST_auth_200_register.png)

![Correo duplicado](images/GA1-EV11/ev11_POST_400_correo_duplicado.png)

![Contraseña débil](images/GA1-EV11/ev11_422_contraseña_debil.png)

![Rol no permitido en registro](images/GA1-EV11/ev11_register_422_rol.png)

![Login correcto](images/GA1-EV11/ev11_POST_login_200.png)

![Cuenta autenticada](images/GA1-EV11/ev11_auth_me_200.png)

![Consulta de mi cuenta sin token: 401](images/GA1-EV11/ev11_auth_me_401.png)

![Token inválido](images/GA1-EV11/ev11_token_invalido_401.png)

### Evidencias de autorización

![Acceso sin token](images/GA1-EV11/ev11_loans_details_sin_token_401.png)

![Usuario sin permiso para consultar detalles](images/GA1-EV11/ev11_loans_detail_user_403.png)

![Acceso como administrador](images/GA1-EV11/ev11_loans_details_admin_200.png)

![Acceso como soporte](images/GA1-EV11/ev11_loans_detail_support_200.png)

![Intento de cambiarse el rol](images/GA1-EV11/ev11_user_cambio_rol_403.png)

![Creación de dispositivo como soporte](images/GA1-EV11/ev11_support_crea_device.png)

![Eliminación denegada a soporte](images/GA1-EV11/ev11_support_delete_device_403.png)

![Eliminación como administrador](images/GA1-EV11/ev11_admin_delete_device_204.png)

![Creación de préstamo](images/GA1-EV11/ev11_user_crea_loan_201.png)

![Creación de dispositivo denegada al rol user: 403](images/GA1-EV11/ev11_user_crea_device_403.png)

![Devolución denegada al usuario](images/GA1-EV11/ev11_user_return_403_loan.png)

![Devolución como soporte](images/GA1-EV11/ev11_support_return_200_loan.png)

### Evidencias de middleware, CORS y límites

![Cabeceras del middleware](images/GA1-EV11/ev11_middleware_headers_200.png)

![Propagación del identificador](images/GA1-EV11/ev11_middlerware_request_id.png)

![Origen permitido](images/GA1-EV11/ev11_cors_origen_permitido_200.png)

![Origen rechazado](images/GA1-EV11/ev11_cors_origen_rechazado_400.png)

![Límite de login](images/GA1-EV11/ev11_rate_limit_login_429.png)

![Fin de la ventana del límite](images/GA1-EV11/ev11_rate_limit_recuperacion_401.png)

### Swagger y OAuth2

![Documentación general](images/GA1-EV11/ev11_swagger_general.png)

![Formulario OAuth2](images/GA1-EV11/ev11_swagger_oauth2.png)

### Reflexión final sobre seguridad

Esta actividad me permitió comprender que una API funcional también necesita controlar quién realiza cada operación. La autenticación identifica al usuario y la autorización determina sus permisos.

El hash protege el almacenamiento de contraseñas, mientras que los tokens permiten realizar peticiones autenticadas durante un tiempo limitado. Las validaciones, las restricciones de la base de datos y los permisos se complementan.

El middleware facilita seguir las peticiones, CORS define los orígenes autorizados para el frontend y los límites de solicitudes ayudan a controlar el abuso. También comprendí que estas herramientas tienen alcances diferentes y que deben comprobarse tanto con respuestas exitosas como con errores.

### Control de versiones y entrega

EV11 se desarrolla en la rama `device_systems_security`. La integración en `develop` y `main` se realizará después de revisar los cambios y las evidencias.

El video de socialización, de máximo 15 minutos, debe explicar las funcionalidades y la seguridad incorporada. Su enlace se agregará después de realizarlo.
