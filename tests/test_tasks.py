from fastapi.testclient import TestClient
import pytest

from backend.main import app, init_db
import backend.main as main_module


@pytest.fixture(autouse=True)
def setup_test_db(tmp_path, monkeypatch):
    """Configura una base de datos aislada temporal para cada prueba."""
    test_db = tmp_path / "test_tareas.db"
    monkeypatch.setattr(main_module, "DB_PATH", test_db)
    monkeypatch.setattr(main_module, "DB_DIR", tmp_path)
    init_db()
    yield


@pytest.fixture
def client():
    """Retorna un cliente de pruebas para la API de FastAPI."""
    with TestClient(app) as c:
        yield c


def test_root(client):
    """Verifica que el endpoint raíz responda correctamente."""
    response = client.get("/")
    assert response.status_code == 200
    assert "mensaje" in response.json()


def test_crear_tarea_exitosa(client):
    """Verifica la creación de tareas con código 201 y valores por defecto."""
    payload = {"titulo": "Comprar leche", "prioridad": "Alta"}
    response = client.post("/tasks", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["titulo"] == "Comprar leche"
    assert data["prioridad"] == "Alta"
    assert data["completada"] is False
    assert "id" in data


def test_crear_tarea_validacion_titulo_vacio(client):
    """Verifica que no se permitan tareas con títulos en blanco."""
    response = client.post("/tasks", json={"titulo": "   ", "prioridad": "Media"})
    assert response.status_code == 422


def test_listar_tareas(client):
    """Verifica el listado de tareas agregadas."""
    client.post("/tasks", json={"titulo": "Tarea 1", "prioridad": "Baja"})
    client.post("/tasks", json={"titulo": "Tarea 2", "prioridad": "Alta"})

    response = client.get("/tasks")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 2


def test_filtrar_tareas_por_completitud_y_prioridad(client):
    """Verifica el filtrado por completada y por prioridad."""
    t1 = client.post("/tasks", json={"titulo": "Tarea 1", "prioridad": "Alta"}).json()
    t2 = client.post("/tasks", json={"titulo": "Tarea 2", "prioridad": "Baja"}).json()
    # Completar la tarea 1
    client.put(f"/tasks/{t1['id']}")

    # Filtrar completadas
    res_completadas = client.get("/tasks?completada=true")
    assert res_completadas.status_code == 200
    assert len(res_completadas.json()) == 1
    assert res_completadas.json()[0]["id"] == t1["id"]

    # Filtrar por prioridad
    res_baja = client.get("/tasks?prioridad=Baja")
    assert res_baja.status_code == 200
    assert len(res_baja.json()) == 1
    assert res_baja.json()[0]["id"] == t2["id"]


def test_toggle_tarea(client):
    """Verifica que el endpoint PUT sin cuerpo alterne el estado de completada."""
    created = client.post("/tasks", json={"titulo": "Hacer ejercicio"}).json()
    task_id = created["id"]
    assert created["completada"] is False

    # Primer toggle -> True
    res_toggle_1 = client.put(f"/tasks/{task_id}")
    assert res_toggle_1.status_code == 200
    assert res_toggle_1.json()["completada"] is True

    # Segundo toggle -> False
    res_toggle_2 = client.put(f"/tasks/{task_id}")
    assert res_toggle_2.status_code == 200
    assert res_toggle_2.json()["completada"] is False


def test_actualizar_tarea_con_cuerpo(client):
    """Verifica la actualización de título y prioridad mediante PUT."""
    created = client.post("/tasks", json={"titulo": "Original", "prioridad": "Baja"}).json()
    task_id = created["id"]

    update_payload = {"titulo": "Actualizado", "prioridad": "Alta"}
    response = client.put(f"/tasks/{task_id}", json=update_payload)
    assert response.status_code == 200
    assert response.json()["titulo"] == "Actualizado"
    assert response.json()["prioridad"] == "Alta"


def test_eliminar_tarea(client):
    """Verifica la eliminación de una tarea existente."""
    created = client.post("/tasks", json={"titulo": "Temporal"}).json()
    task_id = created["id"]

    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["mensaje"] == "Tarea eliminada"

    # Verificar que ya no existe
    res_get = client.get("/tasks")
    assert len(res_get.json()) == 0


def test_tarea_no_encontrada_404(client):
    """Verifica que IDs inexistentes retornen 404 en PUT y DELETE."""
    assert client.put("/tasks/9999").status_code == 404
    assert client.delete("/tasks/9999").status_code == 404
