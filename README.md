# device_systems

## EV09 — FastAPI con SQLAlchemy y persistencia de datos

Actividad **GA1-220501096-01-AA1-EV09**. API REST para gestionar usuarios con FastAPI, SQLAlchemy y SQLite. Permite crear, consultar, filtrar, ordenar, actualizar y eliminar usuarios. Los datos permanecen después de reiniciar el servidor.

La EV07 introdujo las operaciones básicas; la EV08 incorporó el CRUD completo y dependencias. La EV09 reemplaza la lista en memoria por la tabla `users` y añade la fecha de creación.

## Tecnologías

- Python 3.14 o superior, según `pyproject.toml`.
- FastAPI y Uvicorn.
- SQLAlchemy 2 y SQLite.
- Pydantic v2 y email-validator.
- uv para gestionar dependencias.
- Swagger UI, ReDoc, Git y GitHub.

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

## Estructura

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

## Endpoints

| Método | Ruta | Operación | Éxito |
|---|---|---|---|
| GET | `/` | Comprobar funcionamiento | 200 |
| GET | `/users` | Listar, filtrar y ordenar | 200 |
| GET | `/users/{user_id}` | Buscar por ID | 200 |
| POST | `/users/` | Crear usuario | 201 |
| PUT | `/users/{user_id}` | Actualizar todos los campos editables | 200 |
| PATCH | `/users/{user_id}` | Actualizar campos enviados | 200 |
| DELETE | `/users/{user_id}` | Eliminar usuario | 204 sin cuerpo |

Parámetros opcionales del listado:

| Parámetro | Valores | Comportamiento |
|---|---|---|
| `role` | admin, support, user | Filtra por rol |
| `is_active` | true, false | Filtra por estado |
| `ordenar_por` | name, created_at | Orden ascendente; por defecto name |

Los filtros pueden combinarse. El ID sirve como segundo criterio de ordenamiento cuando hay valores iguales.

```text
GET /users?role=support&is_active=false&ordenar_por=name
GET /users?ordenar_por=created_at
```

Las respuestas que pasan por el middleware incluyen `X-App-Name: device_systems` y `X-API-Version: 3.0.0`.

## Ejemplos de peticiones y respuestas

Los IDs y las fechas siguientes son ilustrativos: utilizar el ID real devuelto por POST.

### Crear: POST /users/

```json
{"name":"Laura Gómez","email":"laura@example.com","role":"user","is_active":true}
```

Respuesta 201:

```json
{"id":1,"name":"Laura Gómez","email":"laura@example.com","role":"user","is_active":true,"created_at":"2026-09-21T12:00:00"}
```

GET `/users/1` devuelve ese objeto con 200. GET `/users` devuelve una lista de objetos con esa estructura; si no hay coincidencias, devuelve `[]` con 200.

### Actualizar: PUT /users/1

```json
{"name":"Laura Gómez Actualizada","email":"laura@example.com","role":"support","is_active":false}
```

Devuelve 200 con el usuario completo actualizado, conservando `id` y `created_at`. Omitir un campo requerido produce 422. Mantener el correo propio es válido; usar el de otro usuario produce 400.

### Actualizar parcialmente: PATCH /users/1

```json
{"role":"admin"}
```

Devuelve 200 con el usuario completo; solo cambia el rol. `model_dump(exclude_unset=True)` distingue los campos omitidos de los enviados, incluido `false`. Un cuerpo `{}` produce 400 y un valor explícito `null` produce 422.

### Eliminar: DELETE /users/1

Devuelve 204 sin JSON. Consultar o volver a eliminar ese ID produce 404.

## Manejo de errores

| Código | Caso |
|---|---|
| 400 | Correo duplicado, PATCH vacío o restricción de integridad incumplida |
| 404 | Usuario inexistente en consulta, actualización o eliminación |
| 422 | Nombre, correo, rol, ID o parámetros inválidos; PUT incompleto; PATCH con null |

Ejemplo de usuario inexistente:

```json
{"detail":"El usuario con id 999 no fue encontrado"}
```

Ejemplo de correo duplicado:

```json
{"detail":"El correo electrónico laura@example.com ya está en uso"}
```

Los errores de validación automática incluyen una lista de detalles de Pydantic. Las descripciones `responses` de Swagger documentan los errores; su comportamiento lo implementan las validaciones y `HTTPException`.

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

## Reflexión final

La evolución a SQLite permitió comprender que conservar datos requiere confirmar operaciones en una base de datos. Reiniciar el servidor ya no elimina los usuarios registrados. Separar el modelo SQLAlchemy de los schemas Pydantic ayudó a distinguir el almacenamiento de la validación y de las respuestas HTTP.

Las sesiones y las transacciones permiten agrupar y confirmar cambios; el rollback recupera la sesión cuando falla una restricción. La validación de entrada y las restricciones de la tabla se complementan: Pydantic comprueba el contenido recibido y SQLite protege reglas como la unicidad del correo. La organización en rutas, servicios, modelos y dependencias permitió evolucionar el proyecto conservando sus operaciones REST.

## Control de versiones

EV09 se desarrolla en `feature/fastapi-sqlalchemy-ev09`. Tras revisar y probar los cambios, se integra en `develop`; la versión de entrega se publica en `main`. El historial conserva el desarrollo de las actividades anteriores.
