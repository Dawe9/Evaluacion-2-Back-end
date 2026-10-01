# Preguntas posibles para la interrogacion

## 1. Por que se utiliza un archivo JSON?

Para trabajar con datos ficticios sin depender de una carga inicial en la base de datos. `data_loader.py` abre el archivo y lo convierte en diccionarios y listas de Python.

## 2. Que hace un serializer?

Valida y transforma datos Python para que DRF pueda devolverlos como JSON. En este proyecto se utiliza `serializers.Serializer` porque los datos vienen del JSON y no de consultas a modelos.

## 3. Que hace `@api_view(['GET'])`?

Indica que la funcion es un endpoint de Django REST Framework y que acepta peticiones GET.

## 4. Como se muestra el nombre del profesor?

El curso contiene `teacher_id`. La funcion `courses_with_teacher_name()` crea un diccionario de docentes y busca el nombre correspondiente a cada curso.

## 5. Que hace `fetch()`?

Realiza una peticion HTTP asincrona desde el navegador. Luego `response.json()` convierte la respuesta en datos JavaScript para construir las filas de la tabla.

## 6. Por que la ruta `/` no produce 404?

Porque `academic_project/urls.py` conecta la ruta vacia con `views.home`, que renderiza una plantilla HTML.

## 7. Que representa `StudentCourse`?

Es la tabla intermedia entre estudiantes y cursos. Contiene `student_id` y `course_id`, que forman la clave primaria compuesta del diagrama ER.
# Preguntas para defender el Proyecto 5

## 1. Como se relacionan las instituciones, perfiles y carros?

`Profile.user` es una relación 1:1 con el usuario y guarda su rol y su
institución. `Cart.user` también es 1:1, por lo que el carro queda en la base de
datos y no depende de la sesión ni del dispositivo. `CartItem` relaciona el
carro con un insumo y tiene una restricción única para evitar duplicados.

## 2. Como funciona la autenticación JWT con roles?

`/api/token/` entrega access y refresh. El serializador agrega `role` e
`institution_id` como claims. Los permisos consultan además el rol vigente del
perfil: catálogo público para lectura, `institucion_medica` para el carro y
solicitudes, y `gestor_bodega` para inventario y cambio de estados.

## 3. Que ocurre durante el checkout?

`POST /api/solicitudes/confirmar/` copia las líneas del carro a
`PurchaseRequestItem`, congela nombre comercial, lote, cantidad y precio, crea
la solicitud `pendiente` y vacía el carro dentro de una transacción. El stock
no cambia en esta etapa.

## 4. Cuando se descuenta y repone inventario?

Al cambiar una solicitud a `pagado`, `transaction.atomic()` y
`select_for_update()` bloquean la solicitud y las filas de inventario. Se
comprueba stock y vencimiento antes de descontar. Si una solicitud pagada pasa
a `cancelado`, se reponen las cantidades en otra transacción atómica; un
segundo cambio al mismo estado no vuelve a descontar ni a reponer.

## 5. Como se consulta el catálogo?

`django-filter` permite filtrar `/api/insumos/` con `category`, `price_min`,
`price_max`, `category_name`, `active_ingredient`, `expiration_before` y
`expiration_after`. También hay búsqueda por nombre, principio activo y lote.

## 6. Como se conecta PostgreSQL?

`settings.py` usa `django.db.backends.postgresql` por defecto. Nombre, usuario,
contraseña, host y puerto se leen desde `DB_NAME`, `DB_USER`, `DB_PASSWORD`,
`DB_HOST` y `DB_PORT`; `psycopg` es el driver. SQLite puede usarse solo como base
temporal para pruebas locales, no como configuración de entrega.

## 7. Donde se revisa el contrato de la API?

`drf-spectacular` genera OpenAPI y Swagger está publicado en `/api/docs/`. Desde
esa página se pueden inspeccionar parámetros, autenticación y esquemas de
respuesta.
