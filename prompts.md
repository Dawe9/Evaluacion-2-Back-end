# Registro de prompts

Este archivo conserva los prompts y tareas reales ejecutadas durante el desarrollo del proyecto.
Se evita inventar conversaciones: el contenido a continuacion refleja el trabajo realizado en la sesión de desarrollo.

## Prompt 1: iniciar el proyecto y validar arranque

- Fecha: 2026-09-16
- Herramienta: VS Code terminal / Django
- Prompt exacto: "inicia el proyecto"
- Para que se utilizo: levantar la aplicación Django localmente y comprobar que arranque sin errores.
- Resumen de la respuesta aplicada: se ejecutó `python manage.py runserver` en el entorno virtual y se verificó con la salida de Django que el servidor quedó levantado en http://localhost:8000.

## Prompt 2: corregir errores de sintaxis y arrancar de nuevo

- Fecha: 2026-09-16
- Herramienta: VS Code terminal / Python
- Prompt exacto: "hazlo denuevo"
- Para que se utilizo: corregir la sintaxis rota en `academic/views.py` y volver a iniciar el proyecto.
- Resumen de la respuesta aplicada: se reemplazó la comilla sobrante en la línea de `filtered_product_records` y se validó con `python manage.py check` antes de volver a levantar el servidor.

## Prompt 3: restringir acceso al carrito

- Fecha: 2026-09-16
- Herramienta: VS Code editor / Django
- Prompt exacto: "para el carrito de compra exija tener una cuenta creada"
- Para que se utilizo: exigir autenticación para la compra y evitar que el carrito sea usado por usuarios no registrados.
- Resumen de la respuesta aplicada: se dejó el carrito accesible a usuarios con sesión activa y la validación real de cuenta quedó en el flujo de compra y en la llamada a `/api/orders/`.

## Prompt 4: asociar el carrito a un usuario y perfil

- Fecha: 2026-09-16
- Herramienta: VS Code editor / Django / terminal
- Prompt exacto: "haz que el carrito se asocie a un usuario" y "mi profesor menciono perfiles para asociar el carrito a usuarios"
- Para que se utilizo: crear un perfil de usuario con un carrito persistente para cada cuenta.
- Resumen de la respuesta aplicada: se añadió el modelo `Profile` con `OneToOneField(User)` y un campo `cart = JSONField(default=list)`, además de la API `/api/cart/` para guardar y restaurar el carrito asociado a la cuenta autenticada.

## Prompt 5: corregir persistencia y cierre de sesión

- Fecha: 2026-09-16
- Herramienta: VS Code editor / navegador / terminal
- Prompt exacto: "al cerrar secion se mantiene la compra en el carrito eso no  deveria pasar" y "al volver a iniciar la secion no se guarda lo que ya tenia en el carrito"
- Para que se utilizo: corregir la persistencia del carrito al cerrar e iniciar sesión.
- Resumen de la respuesta aplicada: se ajustó la lógica para mantener el carrito asociado al usuario, restaurarlo con el token JWT y evitar que el estado dependiera solo de `localStorage` sin sincronización con el backend.

## Prompt 6: bloquear agregado sin login

- Fecha: 2026-09-16
- Herramienta: VS Code editor / JavaScript
- Prompt exacto: "por que medeja agregar al carrito siendo que no inicie sesion" y "hazlo"
- Para que se utilizo: impedir que se agreguen productos al carrito si no hay sesión activa.
- Resumen de la respuesta aplicada: se validó `nexo-access-token` antes de ejecutar `addToCart()` y se redirigió a `/login/?next=/products/` cuando no existía sesión autenticada.

## Prompt 7: preparar la aplicación para SaaS multi-tenant

- Fecha: 2026-09-16
- Herramienta: VS Code editor / Django / SQLite
- Prompt exacto: "este proyecto podria convertirse esn saas y tenant ?" y "hazlo"
- Para que se utilizo: añadir una base multi-tenant que permita separar los datos de diferentes clientes u organizaciones.
- Resumen de la respuesta aplicada: se añadieron los modelos `Tenant` y `Profile`; cada usuario obtiene un tenant por defecto, el carrito se guarda en su perfil y las órdenes se asignan y filtran por tenant.

## Prompt 8: verificar el aislamiento por tenant

- Fecha: 2026-09-16
- Herramienta: VS Code editor / Django TestCase / navegador
- Prompt exacto: "comopuedo hacer yo una prueba en la pagina"
- Para que se utilizo: comprobar manualmente el login, la persistencia del carrito y la separación entre cuentas.
- Resumen de la respuesta aplicada: se dejó disponible el servidor en `http://127.0.0.1:8000/` y se documentó el flujo de probar con dos usuarios que cada uno conserve su propio carrito. La prueba automatizada también valida la creación de una orden y su consulta dentro del tenant autenticado.

## Prompt 9: actualizar comentarios y registro de prompts

- Fecha: 2026-09-16
- Herramienta: VS Code editor
- Prompt exacto: "actualiza los comentarios y el archivo propts"
- Para que se utilizo: mantener la documentación del código alineada con el flujo actual de perfiles, carritos persistentes y tenants.
- Resumen de la respuesta aplicada: se actualizaron los docstrings y comentarios de `academic/models.py`, `academic/views.py` y `academic/tests.py`, y se agregaron al registro los prompts de SaaS, pruebas manuales y documentación.

## Prompt 10: revisar y alinear comentarios del proyecto

- Fecha: 2026-10-01
- Herramienta: VS Code editor / documentación del proyecto
- Prompt exacto: "actualiza los comentarios del proyecto"
- Para que se utilizo: revisar la documentación de alto nivel y los comentarios del sistema para reflejar el proyecto actual de farmacia B2B, no la versión académica previa.
- Resumen de la respuesta aplicada: se actualizó la descripción del README para resumir la plataforma actual, se corrigió la estructura de documentación y se dejó el registro de prompts en línea con la evolución del proyecto.
