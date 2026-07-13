# 📝 To-Do List Web App (FastAPI + Vanilla JS)

Aplicación web full-stack para la gestión de tareas con prioridades. 

## 🚀 Tecnologías utilizadas
* **Backend:** Python 3, FastAPI
* **Base de datos:** SQLite
* **Frontend:** HTML5, CSS3, JavaScript Vanilla (Fetch API)

## ⚙️ Instalación y Uso (Entorno Local)

1. Clonar el repositorio.
2. Crear y activar un entorno virtual (Windows):
```powershell
python -m venv venv
.\venv\Scripts\activate
```
3. Instalar las dependencias:
```powershell
pip install fastapi uvicorn
```
4. Levantar el servidor de desarrollo:
```powershell
uvicorn backend.main:app --reload
```
5. Abrir el archivo `frontend/index.html` en el navegador para ver la interfaz.

## 🔐 Endpoints y Documentación
El backend incluye documentación automática generada por Swagger UI. Una vez que el servidor esté corriendo, puedes auditar y probar todos los verbos HTTP (GET, POST, PUT, DELETE) interactuando directamente en:
👉 `http://127.0.0.1:8000/docs`
