# To-Do List Web App
Aplicación web full-stack para gestión de tareas. El frontend será una interfaz sencilla en HTML/JS vanilla, y el backend será una API REST para procesar la información.

## Stack
- Lenguaje: Python 3
- Framework / runtime: FastAPI (Backend)
- Base de datos: SQLite (con librería sqlite3 estándar)
- Frontend: HTML5, CSS3, JavaScript Vanilla (Fetch API)

## Comandos
- `uvicorn main:app --reload` — arranca el servidor de desarrollo en local.
- `pytest` — ejecuta las pruebas unitarias.
- `pip freeze > requirements.txt` — guarda las dependencias del proyecto.

## Estructura del proyecto
- `backend/` — Contiene la lógica de la API (main.py, routers, modelos).
- `frontend/` — Contiene los archivos estáticos (index.html, styles.css, app.js).
- `database/` — Carpeta destinada a guardar el archivo `tareas.db`.

## Convenciones
- Nomenclatura: `snake_case` para variables y funciones en Python, `camelCase` para JavaScript.
- APIs: Todas las respuestas del backend deben devolver un objeto JSON estructurado.
- Manejo de errores: Usar `HTTPException` de FastAPI para respuestas de error claras (404, 400).
- Seguridad: Validar y sanitizar toda entrada del usuario antes de interactuar con la base de datos para evitar SQL Injections.

## No hagas
- No uses ORMs complejos como SQLAlchemy por ahora, mantén las consultas SQL directas y simples con `sqlite3`.
- No instales dependencias externas sin solicitar confirmación previa.
- No modifiques el archivo `agents.md`.
- No reveles rutas absolutas del servidor en los mensajes de error.

## Flujo de trabajo
- Antes de una tarea no trivial, propón un plan y espera mi OK.
- Una tarea a la vez; al terminar, dime qué cambiaste para que lo revise.
- Si no estás seguro al 80%, pregunta. No inventes.

## Documentación
- Seguir la documentación oficial de FastAPI. Las rutas de la API deben estar disponibles en `/docs` (Swagger UI).