// ==========================================================================
// Gestor de Tareas - Lógica del Cliente (JavaScript Vanilla)
// ==========================================================================

// Detección dinámica de URL para permitir ejecución tanto en localhost:8000 como vía file://
const API = window.location.protocol.startsWith('http') 
    ? window.location.origin 
    : 'http://127.0.0.1:8000';

let allTasks = [];
let currentFilter = 'all'; // 'all' | 'pending' | 'completed'

// Elementos del DOM
const taskForm = document.getElementById('taskForm');
const taskInput = document.getElementById('taskInput');
const taskPriority = document.getElementById('taskPriority');
const taskList = document.getElementById('taskList');
const taskCounter = document.getElementById('taskCounter');
const errorBanner = document.getElementById('errorBanner');
const filterButtons = document.querySelectorAll('.filter-btn');

// Asignar clase de estilo de prioridad
function getPrioridadClass(p) {
    if (!p) return 'prioridad-media';
    return 'prioridad-' + p.toLowerCase();
}

// Mostrar mensaje de error si el servidor no responde
function showError(msg) {
    if (!errorBanner) return;
    errorBanner.textContent = msg;
    errorBanner.style.display = 'block';
}

function hideError() {
    if (!errorBanner) return;
    errorBanner.style.display = 'none';
}

// Cargar tareas desde el backend
async function loadTasks() {
    try {
        const res = await fetch(`${API}/tasks`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        allTasks = await res.json();
        hideError();
        renderTasks();
    } catch (err) {
        console.error('Error al cargar tareas:', err);
        showError(`⚠️ No se pudo conectar con la API en ${API}. Verifica que el servidor de FastAPI esté activo.`);
    }
}

// Renderizar tareas según filtro actual
function renderTasks() {
    taskList.innerHTML = '';

    const filtered = allTasks.filter(t => {
        if (currentFilter === 'pending') return !t.completada;
        if (currentFilter === 'completed') return t.completada;
        return true;
    });

    // Actualizar contador
    const pendingCount = allTasks.filter(t => !t.completada).length;
    const completedCount = allTasks.filter(t => t.completada).length;
    taskCounter.textContent = `${pendingCount} pendiente(s), ${completedCount} completada(s)`;

    if (filtered.length === 0) {
        const emptyLi = document.createElement('li');
        emptyLi.className = 'empty-state';
        emptyLi.textContent = currentFilter === 'completed'
            ? 'Aún no has completado ninguna tarea.'
            : currentFilter === 'pending'
            ? '¡Genial! No tienes tareas pendientes 🎉'
            : 'No hay tareas registradas. ¡Agrega una nueva!';
        taskList.appendChild(emptyLi);
        return;
    }

    filtered.forEach(t => {
        const li = document.createElement('li');

        const info = document.createElement('div');
        info.className = 'task-info';

        const badge = document.createElement('span');
        badge.className = 'prioridad ' + getPrioridadClass(t.prioridad);
        badge.textContent = t.prioridad;

        const title = document.createElement('span');
        title.className = 'task-title';
        title.textContent = t.titulo;
        if (t.completada) title.classList.add('completada');

        info.appendChild(badge);
        info.appendChild(title);

        const actions = document.createElement('div');
        actions.className = 'actions';

        const btnToggle = document.createElement('button');
        btnToggle.className = 'btn btn-success';
        btnToggle.textContent = t.completada ? 'Deshacer' : 'Completar';
        btnToggle.setAttribute('aria-label', t.completada ? 'Marcar como pendiente' : 'Marcar como completada');
        btnToggle.addEventListener('click', async () => {
            await toggleTask(t.id);
        });

        const btnDelete = document.createElement('button');
        btnDelete.className = 'btn btn-danger';
        btnDelete.textContent = 'Eliminar';
        btnDelete.setAttribute('aria-label', `Eliminar tarea ${t.titulo}`);
        btnDelete.addEventListener('click', async () => {
            await deleteTask(t.id);
        });

        actions.appendChild(btnToggle);
        actions.appendChild(btnDelete);

        li.appendChild(info);
        li.appendChild(actions);
        taskList.appendChild(li);
    });
}

// Crear nueva tarea
taskForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const titulo = taskInput.value.trim();
    if (!titulo) return;

    try {
        const res = await fetch(`${API}/tasks`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                titulo: titulo,
                prioridad: taskPriority.value
            })
        });
        if (!res.ok) throw new Error('Error al crear tarea');
        taskInput.value = '';
        await loadTasks();
    } catch (err) {
        console.error(err);
        showError('No se pudo guardar la tarea. Intenta de nuevo.');
    }
});

// Alternar estado de completada
async function toggleTask(id) {
    try {
        const res = await fetch(`${API}/tasks/${id}`, { method: 'PUT' });
        if (!res.ok) throw new Error('Error al actualizar tarea');
        await loadTasks();
    } catch (err) {
        console.error(err);
        showError('No se pudo actualizar el estado de la tarea.');
    }
}

// Eliminar tarea
async function deleteTask(id) {
    try {
        const res = await fetch(`${API}/tasks/${id}`, { method: 'DELETE' });
        if (!res.ok) throw new Error('Error al eliminar tarea');
        await loadTasks();
    } catch (err) {
        console.error(err);
        showError('No se pudo eliminar la tarea.');
    }
}

// Manejador de pestañas de filtro
filterButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        filterButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentFilter = btn.dataset.filter;
        renderTasks();
    });
});

// Inicialización
document.addEventListener('DOMContentLoaded', loadTasks);
