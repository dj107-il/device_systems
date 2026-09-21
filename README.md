# device_systems
 
## Descripcion
 
**device_systems** es una API REST construida con **FastAPI** que administra el recurso usuarios del sistema. Permite listar usuarios, consultarlos por id, filtrarlos por rol o estado, registrar usuarios nuevos, actualizar información, realizar modificaciones parciales y eliminar usuarios. El proyecto aplica validaciones mediante **Pydantic v2**, parámetros de ruta y consulta, modelos de respuesta, manejo de errores HTTP y cabeceras HTTP personalizadas.

---

## Tecnologías utilizadas

- python
- FastAPI
- Pydantic v2
- uvicorn
- uv
- Swagger UI
- ReDoc
- Postman / Thunder Client
- Git y Github

---

## Estructura del proyecto

```text
device_systems/
|
|-- app/
|   |- main.py
|   |
|   |- data/
|   |  '- user_db.py
|   |
|   |- dependencies/
|   |  '- user_dependencies.py
|   |
|   |- routes/
|   |  '- user_routes.py
|   |
|   |- schemas/
|   |  '- user_schemas.py
|   |
|   '- services/
|      '- user_services.py
|
|-- images/
|   |- GA1-EV07/
|   |
|   '- GA1-EV08/
|
|- .gitignore
|- .python-version
|- pyproject.toml
|- README.md
|- requirements.txt
'- uv.lock
```

La aplicación se organiza separando las rutas de la API y los esquemas utilizados para validar los datos de los usuarios.

---
 
## Instalacion de dependencias
 
El proyecto usa **uv** para la gestion de dependencias.

para instalar las dependencias del proyecto:
 
```bash
uv sync
```
 
Si prefieres usar pip con un entorno virtual:
 
```bash
python -m venv .venv
.venv\Scripts\activate
pip install fastapi uvicorn pydantic email-validator
```
 
## Ejecucion del servidor
 
```bash
uv run fastapi dev app/main.py
```
 
O con uvicorn directamente:
 
```bash
uv run uvicorn app.main:app --reload
```
 
El servidor queda disponible en: http://127.0.0.1:8000
 
La documentacion interactiva de Swagger UI esta en http://127.0.0.1:8000/docs
 
## Modelo de usuario

El recurso `User` contiene los siguientes campos:

| Campo | Tipo | Descripción |
|---|---|---|
| `id`        | `int`      | Identificador único del usuario |
| `name`      | `str`      | Nombre del usuario |
| `email`     | `EmailStr` | Correo electrónico válido |
| `role`      | `Literal`  | Rol del usuario |
| `is_active` | `bool`     | Estado activo o inactivo |

Los roles permitidos son:

```text
admin
support
user
```

El nombre debe tener como mínimo 3 caracteres y el correo debe cumplir un formato válido.

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
X-API-Version: 1.0
```

---
 
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
  },
  {
    "id": 2,
    "name": "Maria Lopez",
    "email": "maria@example.com",
    "role": "support",
    "is_active": true
  },
  {
    "id": 3,
    "name": "Carlos Garcia",
    "email": "carlos@example.com",
    "role": "user",
    "is_active": false
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

## GET /users/?role=admin

Utiliza un **Query Parameter** para filtrar los usuarios por rol.

Ejemplo:

```text
http://127.0.0.1:8000/users/?role=admin
```

El resultado contiene únicamente los usuarios cuyo rol sea `admin`.

---

## GET /users/?is_active=false

Utiliza un **Query Parameter** para filtrar usuarios según su estado.

Ejemplo:

```text
http://127.0.0.1:8000/users/?is_active=false
```

El resultado contiene los usuarios cuyo estado sea `false`.

---
 
### POST /users
 
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
  "is_active": true
}
```

El sistema valida los datos mediante Pydantic y evita registrar correos electrónicos duplicados.

---
 
### POST /users con correo duplicado
 
Si se intenta registrar un correo que ya existe:
Respuesta (400):
 
**400 Bad Request**

```json
{
  "detail": "El correo electronico ana@example.com ya esta en uso"
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
  "is_active": false
}
```

El usuario conserva su ID y se actualizan sus datos.

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
  "is_active": false
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
- Nombre con mínimo 3 caracteres.
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
GET /users/?role=admin
```

o:

```text
GET /users/?is_active=true
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
X-API-Version: 1.0
```

Estas cabeceras pueden ser consultadas desde Swagger, Postman o cualquier otro cliente HTTP.

---

## Evidencias de pruebas
 
### Swagger UI

- Swagger UI mostrando los endpoints disponibles

![Swagger UI](/images/GA1-EV08/ev08_swagger.png)

---

### GET /users

- Consulta de todos los usuarios:

![GET usuarios](/images/GA1-EV08/ev08_get_usuarios.png)

### GET /users/{user_id}

- Consulta de un usuario mediante Path Parameter:

![GET usuario por id](/images/GA1-EV08/ev08_get_usuario.png)

## GET /users/?role=admin

Filtro de usuarios mediante Query Parameter:

![Filtro por rol](/images/GA1-EV08/ev08_filtro_rol.png)

---

## GET /users/?is_active=false

Filtro de usuarios por estado:

![Filtro por estado](/images/GA1-EV08/ev08_filtro_estado.png)

---

## GET /users/999

Prueba de usuario inexistente:

![GET 404](/images/GA1-EV08/ev08_get_404.png)

---

### POST /users exitoso

- Registro exitoso de un nuevo usuario:

![POST usuario exitoso](/images/GA1-EV08/ev08_post_201.png)

### POST /users con error de validacion

- Prueba de POST /users con error de validacion (correo duplicado o dato invalido)

![POST correo duplicado](/images/GA1-EV08/ev08_post_400.png)
![POST datos invalidos](/images/GA1-EV08/ev08_post_422.png)

---

## PUT /users/{user_id}

Actualización completa de un usuario:

![PUT exitoso](/images/GA1-EV08/ev08_put_200.png)

---

## PATCH /users/{user_id}

Actualización parcial de un usuario:

![PATCH exitoso](/images/GA1-EV08/ev08_patch_200.png)

---

## DELETE /users/{user_id}

Eliminación de un usuario:

![DELETE exitoso](/images/GA1-EV08/ev08_delete_204.png)

---

## ReDoc

Documentación de la API mediante ReDoc:

![ReDoc](/images/GA1-EV08/ev08_redoc1.png)

![ReDoc](/images/GA1-EV08/ev08_redoc2.png)

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

**Ejemplos (con postman):**
 
![Postman GET /users](/images/GA1-EV08/ev08_get_users_postman.png)

![Postman GET /users/{user_id}](/images/GA1-EV08/ev08_users_id_postman.png)

![Postman PATCH error de correo duplicado](/images/GA1-EV08/ev08_correo_duplicado_400_postman.png)

![Postman DELETE /users/{user_id}](/images/GA1-EV08/ev08_delete_404_postman.png)

---

# Dependency Injection

En el proyecto se aplicó **Dependency Injection (DI)** mediante la función `Depends()` proporcionada por FastAPI.

Se creó una dependencia llamada `obtener_usuario_o_404` en el módulo `app/dependencies/user_dependencies.py`. Esta función recibe el `user_id`, busca el usuario mediante la capa de servicios y devuelve el usuario encontrado. Si el usuario no existe, se genera una respuesta `404 Not Found`.

```python
def obtener_usuario_o_404(user_id: int) -> User:
    return buscar_usuario_por_id(user_id)
```

Esta dependencia se utiliza en los endpoints que necesitan obtener un usuario específico. Mediante Depends(), FastAPI se encarga de ejecutar la dependencia y proporcionar el resultado directamente al endpoint.

Por ejemplo:

```python
usuario: User = Depends(obtener_usuario_o_404)
```

De esta manera, la lógica para buscar un usuario y controlar su existencia no necesita repetirse en cada endpoint. Esto permite separar responsabilidades, reducir código repetido y facilitar el mantenimiento del proyecto.

# Reflexión final sobre la evolución del proyecto

El proyecto `device_systems` evolucionó progresivamente desde una API básica hasta una aplicación backend con una estructura más organizada y funcionalidades orientadas a un escenario real de gestión de usuarios.

Inicialmente se trabajó con la configuración básica de FastAPI y la creación de los primeros endpoints. Posteriormente se incorporaron modelos con Pydantic v2 para validar la información recibida, parámetros de ruta y consulta para realizar búsquedas y filtros, y diferentes métodos HTTP para gestionar las operaciones sobre los usuarios.

A medida que avanzó el proyecto también se implementaron Response Models, manejo estructurado de errores, códigos de estado HTTP, cabeceras personalizadas y Dependency Injection mediante `Depends()`. Esto permitió comprender que una API no consiste únicamente en crear endpoints, sino también en organizar correctamente sus responsabilidades y controlar la información que recibe y devuelve.

Finalmente, las pruebas realizadas mediante Swagger UI y clientes HTTP permitieron comprobar tanto los casos exitosos como los diferentes escenarios de error. Esta evolución permitió pasar de una implementación funcional básica a una API REST más estructurada, validada, documentada y preparada para futuras ampliaciones.

# Reflexión sobre el uso de FastAPI

Desarrollar `device_systems` me permitió entender de forma práctica cómo FastAPI facilita la construcción de APIs REST. Organizar el proyecto separando esquemas (`schemas`), rutas (`routes`), servicios (`services`), datos (`data`) y dependencias (`dependencies`) me ayudó a mantener el código ordenado y fácil de escalar si se agregan más recursos además de usuarios.

El uso de Pydantic v2 fue clave para las validaciones: definir restricciones como el mínimo de caracteres en el nombre, el formato de correo con `EmailStr` y los valores permitidos en el rol con `Literal` evitó tener que escribir validaciones manuales. Además, los errores `422` se generan automáticamente cuando los datos recibidos no cumplen con el esquema definido.

Trabajar con Path Parameters y Query Parameters me permitió comprender la diferencia entre identificar un recurso específico mediante su ID y filtrar una colección de usuarios mediante criterios como el rol o el estado activo.

Finalmente, separar el modelo de entrada (`UserCreate`) del modelo de respuesta (`User`), implementar Response Models, manejar errores HTTP y utilizar cabeceras HTTP personalizadas mediante middleware permitió comprender la importancia de controlar exactamente qué información recibe y expone una API hacia el cliente.
 
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
- Organización modular mediante rutas, esquemas, servicios, datos y dependencias.