import sqlite3
import os
from enum import Enum
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "tareas.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        """CREATE TABLE IF NOT EXISTS tareas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            completada INTEGER NOT NULL DEFAULT 0,
            prioridad TEXT NOT NULL DEFAULT 'Media'
        )"""
    )
    try:
        conn.execute("ALTER TABLE tareas ADD COLUMN prioridad TEXT NOT NULL DEFAULT 'Media'")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()


class Prioridad(str, Enum):
    Alta = "Alta"
    Media = "Media"
    Baja = "Baja"


class TareaIn(BaseModel):
    titulo: str
    prioridad: Prioridad = Prioridad.Media

    @field_validator("titulo")
    @classmethod
    def titulo_no_vacio(cls, v):
        if not v.strip():
            raise ValueError("El título no puede estar vacío")
        return v.strip()


class TareaOut(BaseModel):
    id: int
    titulo: str
    completada: bool
    prioridad: Prioridad


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def root():
    return {"mensaje": "API de tareas funcionando"}


@app.get("/tasks")
def listar_tareas():
    conn = get_db()
    rows = conn.execute(
        "SELECT id, titulo, completada, prioridad FROM tareas"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.post("/tasks", response_model=TareaOut)
def crear_tarea(tarea: TareaIn):
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO tareas (titulo, prioridad) VALUES (?, ?)",
        (tarea.titulo, tarea.prioridad.value),
    )
    conn.commit()
    tarea_id = cur.lastrowid
    conn.close()
    return {"id": tarea_id, "titulo": tarea.titulo, "completada": False, "prioridad": tarea.prioridad}


@app.put("/tasks/{task_id}", response_model=TareaOut)
def toggle_tarea(task_id: int):
    conn = get_db()
    row = conn.execute(
        "SELECT id, titulo, completada, prioridad FROM tareas WHERE id = ?",
        (task_id,),
    ).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    nuevo_estado = 0 if row["completada"] else 1
    conn.execute(
        "UPDATE tareas SET completada = ? WHERE id = ?", (nuevo_estado, task_id)
    )
    conn.commit()
    conn.close()
    return {
        "id": row["id"],
        "titulo": row["titulo"],
        "completada": bool(nuevo_estado),
        "prioridad": row["prioridad"],
    }


@app.delete("/tasks/{task_id}")
def eliminar_tarea(task_id: int):
    conn = get_db()
    row = conn.execute(
        "SELECT id FROM tareas WHERE id = ?", (task_id,)
    ).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    conn.execute("DELETE FROM tareas WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return {"mensaje": "Tarea eliminada"}
