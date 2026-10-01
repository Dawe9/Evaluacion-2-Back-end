# Proyecto 5: Pedidos de Insumos Médicos y Farmacia

## Preparación

Instala las dependencias y crea una base PostgreSQL vacía llamada `farmacia_b2b`.
La aplicación usa PostgreSQL de forma predeterminada; configura la conexión en el
entorno antes de ejecutar Django:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:DB_NAME = "farmacia_b2b"
$env:DB_USER = "postgres"
$env:DB_PASSWORD = "<contraseña local>"
$env:DB_HOST = "localhost"
$env:DB_PORT = "5432"
$env:DJANGO_DEBUG = "true"
$env:STUDENT_NAME = "Nombre completo"
$env:STUDENT_SECTION = "Sección"
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py seed_demo_supplies
.\.venv\Scripts\python.exe manage.py runserver
```

`seed_demo_supplies` crea tres categorías y ocho insumos de ejemplo con lotes,
stock, precios y URLs de imágenes. Es seguro ejecutarlo más de una vez: actualiza
los ejemplos por su nombre y lote sin crear duplicados. Las imágenes se cargan
desde URLs externas; puedes reemplazarlas luego desde el formulario del panel de
administración.

En el panel `/admin/`, crea las instituciones médicas, categorías e insumos con
nombre comercial, principio activo, lote, vencimiento, precio por caja, imagen
opcional y stock. Cada cuenta debe tener un `Profile`: asigna el rol
`institucion_medica` y su institución a los clientes; asigna
`gestor_bodega` a la cuenta de bodega. El usuario debe existir antes de crear su
perfil.

El superusuario puede asignar administradores de página desde **Usuarios**:
activa `Staff status` (`is_staff`) y asigna el perfil `gestor_bodega`. Al volver a
iniciar sesión, esa cuenta podrá gestionar el catálogo desde `/admin/` o el
`Panel de administración` en `/gestor/`, que incluye un botón para abrir la
documentación en `/api/docs/`. Solo los superusuarios
pueden promover usuarios a staff/superusuario y asignar el rol `gestor_bodega`.
Los administradores secundarios pueden crear cuentas normales de trabajadores y
asociarlas opcionalmente a una institución, pero no pueden conceder privilegios
de administrador. El admin no permite cambiar directamente el estado de las
solicitudes para conservar la validación transaccional del inventario.

## Flujo de negocio

Las instituciones consultan el catálogo público, agregan insumos y cantidades a
su carro persistente y confirman la solicitud. El checkout crea una solicitud
`pendiente`, guarda nombre/lote/precio de cada línea y vacía el carro, sin
reservar ni descontar inventario. El gestor cambia su estado a `pagado`; solo
entonces se valida vencimiento y stock, y el descuento se realiza dentro de una
transacción. Una solicitud pagada puede pasar a `entregado` o `cancelado`; al
cancelarla, las cantidades se reponen de forma atómica.

## API

- `GET /api/categorias/` y `GET /api/insumos/`: lectura pública.
- `GET /api/insumos/?category=1&price_min=1000&price_max=5000`: filtros por categoría y precio.
- `POST /api/carro-insumos/`, `GET /api/carro-insumos/` y `DELETE /api/carro-insumos/?supply_id=1`: carro de la institución autenticada.
- `POST /api/solicitudes/confirmar/`: checkout de la institución autenticada.
- `GET /api/mis-solicitudes/`: historial de la institución autenticada.
- `GET /api/solicitudes/` y `PATCH /api/solicitudes/<id>/estado/`: gestión para el rol `gestor_bodega`.
- `POST /api/token/` y `POST /api/token/refresh/`: JWT access/refresh; los claims incluyen `role` e `institution_id`.
- `/register/` y `POST /api/registro/`: alta pública de una institución médica y su cuenta cliente.
- `/api/docs/`: documentación Swagger/OpenAPI.
- `/gestor/`: interfaz de inventario y gestión de solicitudes para `gestor_bodega`.

El gestor crea, edita y elimina categorías e insumos mediante la API o el panel
administrativo. Las escrituras de catálogo y los cambios de estado están
protegidos por rol.

## Pruebas

Las pruebas automatizadas pueden usar SQLite solo como base temporal de test; la
configuración normal de la aplicación continúa usando PostgreSQL:

```powershell
$env:DB_ENGINE = "django.db.backends.sqlite3"
$env:DB_NAME = ":memory:"
.\venv\Scripts\python.exe manage.py test
Remove-Item Env:DB_ENGINE
Remove-Item Env:DB_NAME
```

El footer toma el nombre y la sección de `STUDENT_NAME` y `STUDENT_SECTION` y
muestra el año actual. Configura esos dos valores en el entorno antes de la
entrega.