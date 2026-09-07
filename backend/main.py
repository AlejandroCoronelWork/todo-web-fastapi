from contextlib import asynccontextmanager
from enum import Enum
import os
from pathlib import Path
import sqlite3
from typing import Any

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, field_validator

# ------------------------------------------------------------------------------
# CONFIGURACIÓN DE BASE DE DATOS Y RUTAS
# ------------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "database"
DB_PATH = DB_DIR / "tareas.db"
FRONTEND_DIR = BASE_DIR / "frontend"


def get_db() -> sqlite3.Connection:
    """Retorna una conexión a la base de datos SQLite configurada."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Inicializa la tabla de tareas y aplica migraciones si es necesario."""
    conn = get_db()
    conn.execute(
        """CREATE TABLE IF NOT EXISTS tareas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            completada INTEGER NOT NULL DEFAULT 0,
            prioridad TEXT NOT NULL DEFAULT 'Media'
        )"""
    )
    # Migración retrocompatible para instalaciones previas sin columna prioridad
    try:
        conn.execute("ALTER TABLE tareas ADD COLUMN prioridad TEXT NOT NULL DEFAULT 'Media'")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestor de ciclo de vida moderno para FastAPI (reemplaza startup obsoleto)."""
    init_db()
    yield


# ------------------------------------------------------------------------------
# INICIALIZACIÓN DE LA APLICACIÓN FASTAPI
# ------------------------------------------------------------------------------
app = FastAPI(
    title="To-Do List API",
    description="API REST para gestión de tareas con prioridades y persistencia en SQLite.",
    version="1.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar frontend estático si existe
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


# ------------------------------------------------------------------------------
# MODELOS Y ESQUEMAS PYDANTIC
# ------------------------------------------------------------------------------
class Prioridad(str, Enum):
    Alta = "Alta"
    Media = "Media"
    Baja = "Baja"


class TareaIn(BaseModel):
    titulo: str
    prioridad: Prioridad = Prioridad.Media

    @field_validator("titulo")
    @classmethod
    def titulo_no_vacio(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El título no puede estar vacío")
        return v.strip()


class TareaUpdate(BaseModel):
    titulo: str | None = None
    prioridad: Prioridad | None = None
    completada: bool | None = None

    @field_validator("titulo")
    @classmethod
    def titulo_no_vacio(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("El título no puede estar vacío")
        return v.strip() if v is not None else None


class TareaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    titulo: str
    completada: bool
    prioridad: Prioridad


# ------------------------------------------------------------------------------
# ENDPOINTS REST
# ------------------------------------------------------------------------------
@app.get("/", tags=["General"])
def root() -> dict[str, str]:
    """Endpoint de comprobación de salud y estado de la API."""
    return {"mensaje": "API de tareas funcionando", "docs": "/docs"}


@app.get("/tasks", response_model=list[TareaOut], tags=["Tareas"])
def listar_tareas(
    completada: bool | None = Query(None, description="Filtrar por estado de completitud"),
    prioridad: Prioridad | None = Query(None, description="Filtrar por prioridad (Alta, Media, Baja)"),
) -> list[dict[str, Any]]:
    """Obtiene la lista de tareas con soporte de filtros opcionales."""
    conn = get_db()
    query = "SELECT id, titulo, completada, prioridad FROM tareas WHERE 1=1"
    params: list[Any] = []

    if completada is not None:
        query += " AND completada = ?"
        params.append(1 if completada else 0)

    if prioridad is not None:
        query += " AND prioridad = ?"
        params.append(prioridad.value)

    query += " ORDER BY id DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()

    return [
        {
            "id": r["id"],
            "titulo": r["titulo"],
            "completada": bool(r["completada"]),
            "prioridad": r["prioridad"],
        }
        for r in rows
    ]


@app.post("/tasks", response_model=TareaOut, status_code=status.HTTP_201_CREATED, tags=["Tareas"])
def crear_tarea(tarea: TareaIn) -> dict[str, Any]:
    """Crea una nueva tarea con título y prioridad."""
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO tareas (titulo, prioridad) VALUES (?, ?)",
        (tarea.titulo, tarea.prioridad.value),
    )
    conn.commit()
    tarea_id = cur.lastrowid
    conn.close()

    return {
        "id": tarea_id,
        "titulo": tarea.titulo,
        "completada": False,
        "prioridad": tarea.prioridad,
    }


@app.put("/tasks/{task_id}", response_model=TareaOut, tags=["Tareas"])
def actualizar_o_toggle_tarea(task_id: int, datos: TareaUpdate | None = None) -> dict[str, Any]:
    """Actualiza una tarea. Si no se envía cuerpo, alterna (toggle) el estado completado."""
    conn = get_db()
    row = conn.execute(
        "SELECT id, titulo, completada, prioridad FROM tareas WHERE id = ?",
        (task_id,),
    ).fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada")

    # Si no se proveen datos o todos son None, se alterna completada (comportamiento toggle clásico)
    if datos is None or (datos.titulo is None and datos.prioridad is None and datos.completada is None):
        nuevo_completada = 0 if row["completada"] else 1
        nuevo_titulo = row["titulo"]
        nuevo_prioridad = row["prioridad"]
    else:
        nuevo_completada = (1 if datos.completada else 0) if datos.completada is not None else row["completada"]
        nuevo_titulo = datos.titulo if datos.titulo is not None else row["titulo"]
        nuevo_prioridad = datos.prioridad.value if datos.prioridad is not None else row["prioridad"]

    conn.execute(
        "UPDATE tareas SET titulo = ?, prioridad = ?, completada = ? WHERE id = ?",
        (nuevo_titulo, nuevo_prioridad, nuevo_completada, task_id),
    )
    conn.commit()
    conn.close()

    return {
        "id": task_id,
        "titulo": nuevo_titulo,
        "completada": bool(nuevo_completada),
        "prioridad": nuevo_prioridad,
    }


@app.delete("/tasks/{task_id}", tags=["Tareas"])
def eliminar_tarea(task_id: int) -> dict[str, Any]:
    """Elimina una tarea por su ID."""
    conn = get_db()
    row = conn.execute("SELECT id FROM tareas WHERE id = ?", (task_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada")

    conn.execute("DELETE FROM tareas WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return {"mensaje": "Tarea eliminada", "id": task_id}
