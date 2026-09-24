# device_systems

## Descripción

**device_systems** es una API REST construida con **FastAPI** que administra el recurso usuarios del sistema. Permite listar usuarios, consultarlos por id, filtrarlos por rol o estado, registrar usuarios nuevos, actualizar información, realizar modificaciones parciales y eliminar usuarios. El proyecto aplica validaciones mediante **Pydantic v2**, parámetros de ruta y consulta, modelos de respuesta, manejo de errores HTTP y cabeceras HTTP personalizadas.


En la actividad **GA1-220501096-01-AA1-EV09**, se incorpora persistencia mediante **SQLAlchemy y SQLite**. Los usuarios se guardan en la tabla `users` y permanecen después de reiniciar el servidor. Se conservan las funcionalidades de EV07 y EV08.

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
- SQLite

---

## Estructura del proyecto

```text
device_systems/
├── app/
│   ├── main.py
│   ├── database/connection.py
│   ├── models/user_model.py
│   ├── schemas/user_schemas.py
│   ├── routes/user_routes.py
│   ├── services/user_services.py
│   └── dependencies/
│       ├── database_dependency.py
│       └── user_dependencies.py
├── images/
│   ├── GA1-EV07/
│   ├── GA1-EV08/
│   └── GA1-EV09/
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
uv run uvicorn app.main:app --reload
```

Alternativa con Python 3.14 y pip:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Ejecutar siempre desde la raíz del proyecto. La URL `sqlite:///./device_systems.db` utiliza el directorio de ejecución. Al cargar la aplicación, `Base.metadata.create_all(bind=engine)` crea las tablas inexistentes. Una instalación nueva comienza sin usuarios; se crean mediante POST.

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

Todas las respuestas incluyen las cabeceras personalizadas X-App-Name y X-API-Version.

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

Los IDs y fechas de los ejemplos son ilustrativos. Una base nueva comienza vacía: primero crea usuarios con POST y utiliza los IDs que devuelva la API.

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

Permite registrar un nuevo usuario.

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
| `201` | Created | Creación exitosa de un usuario |
| `204` | No Content | Eliminación exitosa |
| `400` | Bad Request | Datos o acciones no permitidas |
| `404` | Not Found | Usuario inexistente |
| `422` | Unprocessable Entity | Datos que no cumplen las validaciones |

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

Pendiente de adjuntar a las evidencias EV09: capturas específicas de GET exitoso del listado y de consulta por ID. Las capturas de [EV07](images/GA1-EV07/) y [EV08](images/GA1-EV08/) se conservan como antecedentes; no sustituyen las evidencias de persistencia de esta versión.

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
