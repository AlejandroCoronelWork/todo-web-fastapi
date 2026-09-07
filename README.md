# 📝 To-Do List Web App (FastAPI + Vanilla JS)

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-Vanilla%20ES6%2B-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![Tests](https://img.shields.io/badge/Tests-Pytest%20(9%2F9%20passed)-brightgreen?style=for-the-badge&logo=pytest&logoColor=white)
![License](https://img.shields.io/badge/License-Academic%20%26%20Educational-blue?style=for-the-badge)

---

## 📌 Descripción General

Aplicación web *full-stack* moderna y ligera para la gestión de tareas con prioridades (*Alta*, *Media*, *Baja*). El proyecto implementa una **API REST** asíncrona construida sobre **FastAPI** con persistencia en **SQLite** y un cliente web reactivo desacoplado en **HTML5, CSS3 y JavaScript Vanilla** utilizando Fetch API.

---

## ✨ Características Principales

* **CRUD Completo de Tareas**: Crear, listar, actualizar estado/prioridad y eliminar tareas en tiempo real.
* **Sistema de Prioridades**: Clasificación visual en tres niveles (*Alta*, *Media*, *Baja*) con badges estilizados.
* **Filtros en el Cliente**: Pestañas de filtrado dinámico (*Todas*, *Pendientes*, *Completadas*) sin recargar la página.
* **Contador en Tiempo Real**: Métricas visibles de tareas pendientes y completadas.
* **Validación de Datos con Pydantic v2**: Validación estricta en el servidor para evitar títulos vacíos o prioridades inválidas.
* **Documentación Interactiva Automática**: Swagger UI y ReDoc integrados nativamente.
* **Pruebas Automatizadas**: Suite completa de tests unitarios y de integración con `pytest` y `TestClient`.

---

## 📂 Estructura del Proyecto

```text
todo-web-fastapi/
├── backend/
│   └── main.py          # API REST, configuración CORS, ciclo lifespan y SQLite
├── database/
│   └── .gitkeep         # Directorio local para tareas.db (ignorado en git)
├── frontend/
│   ├── index.html       # Estructura semántica accesible
│   ├── styles.css       # Diseño moderno con variables CSS y transiciones
│   └── app.js           # Lógica cliente, Fetch API y renderizado dinámico
├── tests/
│   └── test_tasks.py    # Suite de pruebas unitarias con base de datos aislada
├── requirements.txt     # Dependencias del proyecto
├── agents.md            # Convenciones y contexto del proyecto
└── README.md            # Documentación general
```

---

## 🚀 Puesta en Marcha

### Prerrequisitos
* Python 3.10 o superior instalado.
* Navegador web moderno.

### 1. Clonar el repositorio
```bash
git clone https://github.com/aledash3/todo-web-fastapi.git
cd todo-web-fastapi
```

### 2. Crear y activar entorno virtual

**En Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**En Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Iniciar el servidor backend
```bash
uvicorn backend.main:app --reload
```
El servidor arrancará en `http://127.0.0.1:8000`.

### 5. Abrir la aplicación frontend
Tienes dos formas sencillas de usar la interfaz:
* **Opción A (Recomendada)**: Navega a `http://127.0.0.1:8000/static/index.html` (servida directamente por FastAPI).
* **Opción B**: Haz doble clic en el archivo `frontend/index.html` para abrirlo en tu navegador.

---

## 🧪 Ejecución de Pruebas

El proyecto cuenta con una suite de pruebas automatizadas que utiliza bases de datos temporales aisladas:

```bash
pytest -v
```

---

## 🔌 Especificación de la API REST

La documentación Swagger interactiva está disponible en: 👉 **`http://127.0.0.1:8000/docs`**

| Método | Endpoint | Descripción | Código Éxito |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Comprobación de salud y estado de la API | `200 OK` |
| `GET` | `/tasks` | Lista tareas (admite `?completada=bool` y `?prioridad=str`) | `200 OK` |
| `POST` | `/tasks` | Crea una nueva tarea (`titulo`, `prioridad`) | `201 Created` |
| `PUT` | `/tasks/{id}` | Alterna completada o actualiza campos enviados | `200 OK` |
| `DELETE` | `/tasks/{id}` | Elimina una tarea por su ID | `200 OK` |

---

## 👨‍💻 Autores y Atribución Académica

* **Carlos Alejandro Coronel Quilachamin**
* **David Alejandro Cruz Palacios**

*Universidad Politécnica Salesiana — Ecuador*

---

## 📜 Licencia

Este proyecto fue desarrollado exclusivamente con fines **académicos y educativos**. Todos los derechos pertenecen a sus respectivos autores. Queda prohibida su explotación comercial sin autorización expresa.
