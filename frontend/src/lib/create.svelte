<script>
import { onMount } from 'svelte';

// Closets
let closetName = $state('');
let closetError = $state('');
let closetSuccess = $state('');
let closetLoading = $state(false);
let closets = $state([]);
let selectedCloset = $state(null);

// Cajones
let drawerName = $state('');
let drawerType = $state('');
let drawerSize = $state('');
let drawerCapacity = $state('');
let drawerError = $state('');
let drawerSuccess = $state('');
let drawerLoading = $state(false);
let drawers = $state([]);

// Objetos
let objectName = $state('');
let objectType = $state('');
let objectSize = $state('');
let objectError = $state('');
let objectSuccess = $state('');
let objectLoading = $state(false);
let objects = $state([]);

// Cargar closets y objetos al inicio
onMount(async () => {
    await fetchClosets();
    await fetchObjects();
});

async function fetchClosets() {
    closetError = '';
    try {
        const res = await fetch('http://localhost:8000/app/closets/', {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
            mode: 'cors',
        });
        
        if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
        }
        
        const data = await res.json();
        
        // Forzar reactividad con $state
        if (Array.isArray(data)) {
            closets = [...data];
        } else {
            closets = [];
        }
        
        // Si el closet seleccionado ya no existe, selecciona el primero
        if (closets.length === 0) {
            selectedCloset = null;
            drawers = [];
        } else if (!selectedCloset || !closets.find(c => c.id === selectedCloset.id)) {
            selectCloset(closets[0]);
        }
    } catch (e) {
        console.error('Error fetching closets:', e);
        closetError = `Error al cargar closets: ${e.message}`;
        closets = [];
    }
}

async function selectCloset(closet) {
    selectedCloset = closet;
    await fetchDrawers(closet.id);
}

async function fetchDrawers(closetId) {
    try {
        const res = await fetch(`http://localhost:8000/app/drawers/?closet=${closetId}`);
        if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
        }
        const data = await res.json();
        
        // Forzar reactividad con $state
        drawers = Array.isArray(data) ? [...data] : [];
    } catch (e) {
        console.error('Error fetching drawers:', e);
        drawerError = 'No se pudieron cargar los cajones';
        drawers = [];
    }
}

async function fetchAllDrawers() {
    // Para el select de objetos (mostrar todos los cajones de todos los closets)
    try {
        const res = await fetch('http://localhost:8000/app/drawers/');
        return await res.json();
    } catch (e) {
        return [];
    }
}

async function fetchObjects() {
    try {
        const res = await fetch('http://localhost:8000/app/objects/');
        if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
        }
        const data = await res.json();
        
        // Forzar reactividad con $state
        objects = Array.isArray(data) ? [...data] : [];
    } catch (e) {
        console.error('Error fetching objects:', e);
        objects = [];
    }
}

// Crear closet
async function createCloset(e) {
    e.preventDefault();
    closetError = '';
    closetSuccess = '';
    closetLoading = true;
    try {
        const res = await fetch('http://localhost:8000/app/closets/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: closetName, drawers: [] })
        });
        if (!res.ok) {
            const data = await res.json();
            throw new Error(data.error || 'Error al crear el closet');
        }
        closetName = '';
        closetSuccess = '¡Closet creado!';
        
        // Intentar recargar, pero no fallar si hay error
        try {
            await fetchClosets();
        } catch (fetchError) {
            console.warn('Error recargando closets:', fetchError);
        }
    } catch (e) {
        closetError = e.message;
    } finally {
        closetLoading = false;
    }
}

// Crear cajón
async function createDrawer(e) {
    e.preventDefault();
    drawerError = '';
    drawerSuccess = '';
    drawerLoading = true;
    try {
        const res = await fetch('http://localhost:8000/app/drawers/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: drawerName,
                type: drawerType,
                size: drawerSize,
                max_capacity: drawerCapacity,
                closet: selectedCloset.id
            })
        });
        if (!res.ok) {
            const data = await res.json();
            throw new Error(data.error || 'Error al crear el cajón');
        }
        drawerName = '';
        drawerType = '';
        drawerSize = '';
        drawerCapacity = '';
        drawerSuccess = '¡Cajón agregado!';
        
        // Intentar recargar, pero no fallar si hay error
        try {
            await fetchDrawers(selectedCloset.id);
        } catch (fetchError) {
            console.warn('Error recargando cajones:', fetchError);
        }
    } catch (e) {
        drawerError = e.message;
    } finally {
        drawerLoading = false;
    }
}

// Crear objeto libre (sin asignar a cajón)
async function createObject(e) {
    e.preventDefault();
    objectError = '';
    objectSuccess = '';
    objectLoading = true;
    try {
        // Crear objeto sin asignar a cajón
        const res = await fetch('http://localhost:8000/app/objects/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                name: objectName, 
                type: objectType, 
                size: objectSize
                // No incluimos drawer - el objeto queda libre
            })
        });
        if (!res.ok) {
            const data = await res.json();
            throw new Error(data.error || 'Error al crear el objeto');
        }
        
        // Limpiar campos
        objectName = '';
        objectType = '';
        objectSize = '';
        objectSuccess = '¡Objeto creado exitosamente! Ahora está disponible para asignar a cualquier cajón.';
        
        // Intentar actualizar lista de objetos, pero no fallar si hay error
        try {
            await fetchObjects();
        } catch (fetchError) {
            console.warn('Error recargando objetos:', fetchError);
        }
    } catch (e) {
        objectError = e.message;
    } finally {
        objectLoading = false;
    }
}

const typeOptions = [
    { value: 'C', label: 'Ropa 👔' },
    { value: 'P', label: 'Papeles 📋' },
    { value: 'W', label: 'Cables ⚡' }
];
const sizeOptions = [
    { value: 'S', label: 'Pequeño' },
    { value: 'M', label: 'Mediano' },
    { value: 'L', label: 'Grande' }
];

</script>

<header class="page-header">
    <div class="header-content">
        <h1>📝 Panel de Creación</h1>
        <nav class="header-nav">
            <button 
                class="nav-link"
                onclick={() => window.navigate('/')}
            >
                🏠 Ir a Homepage
            </button>
        </nav>
    </div>
</header>

<div class="dashboard-container">
    <div class="dashboard-left">
        <h3>Armarios</h3>
        <form onsubmit={createCloset} class="create-form">
            <div class="form-group">
                <label for="closetName">Nombre del closet</label>
                <input id="closetName" type="text" bind:value={closetName} required placeholder="Ej: Armario de Roble" />
            </div>
            <button type="submit" disabled={closetLoading}>{closetLoading ? 'Creando...' : 'Crear closet'}</button>
            {#if closetError}
                <div class="error">{closetError}</div>
            {/if}
            {#if closetSuccess}
                <div class="success">{closetSuccess}</div>
            {/if}
        </form>
        <div class="closets-list">
            <div class="closets-header">
                <h4>Lista de closets (Total: {closets.length})</h4>
                <button type="button" class="reload-btn" onclick={fetchClosets}>🔄 Recargar</button>
            </div>
            {#if closetError}
                <div class="error">Error: {closetError}</div>
            {/if}
            {#if !closets || closets.length === 0}
                <div class="empty-list">No hay closets registrados.</div>
            {/if}
            {#if closets && closets.length > 0}
                <ul>
                    {#each closets as c, index}
                        <li class:selected={selectedCloset && c.id === selectedCloset.id} onclick={() => selectCloset(c)}>
                            {index + 1}. {c.name}
                        </li>
                    {/each}
                </ul>
            {/if}
        </div>
    </div>
    <div class="dashboard-center">
        <h3>Cajones del closet seleccionado</h3>
        {#if selectedCloset}
            <div class="selected-closet-info">
                <h4>📁 {selectedCloset.name}</h4>
                <p class="closet-details">Cajones: {drawers.length}</p>
            </div>
            
            <form onsubmit={createDrawer} class="create-form">
                <div class="form-group">
                    <label for="drawerName">Nombre del cajón</label>
                    <input id="drawerName" type="text" bind:value={drawerName} required placeholder="Ej: Cajón de Camisetas" />
                </div>
                <div class="form-group">
                    <label for="drawerType">Tipo</label>
                    <select id="drawerType" bind:value={drawerType} required>
                        <option value="" disabled selected>Selecciona un tipo</option>
                        {#each typeOptions as opt}
                            <option value={opt.value}>{opt.label}</option>
                        {/each}
                    </select>
                </div>
                <div class="form-group">
                    <label for="drawerSize">Tamaño</label>
                    <select id="drawerSize" bind:value={drawerSize} required>
                        <option value="" disabled selected>Selecciona un tamaño</option>
                        {#each sizeOptions as opt}
                            <option value={opt.value}>{opt.label}</option>
                        {/each}
                    </select>
                </div>
                <div class="form-group">
                    <label for="drawerCapacity">Capacidad máxima</label>
                    <input id="drawerCapacity" type="number" min="1" bind:value={drawerCapacity} required placeholder="Ej: 10" />
                </div>
                <button type="submit" disabled={drawerLoading}>{drawerLoading ? 'Agregando...' : 'Agregar cajón'}</button>
                {#if drawerError}
                    <div class="error">{drawerError}</div>
                {/if}
                {#if drawerSuccess}
                    <div class="success">{drawerSuccess}</div>
                {/if}
            </form>
            
            <div class="drawers-list">
                <h4>Cajones en este armario</h4>
                {#if drawers.length === 0}
                    <div class="empty-list">No hay cajones en este armario.</div>
                {:else}
                    <div class="drawers-grid">
                        {#each drawers as d}
                            <div class="drawer-card">
                                <div class="drawer-header">
                                    <span class="drawer-icon">📦</span>
                                    <strong>{d.name}</strong>
                                </div>
                                <div class="drawer-details">
                                    <span class="drawer-type">{d.get_type_display || d.type}</span>
                                    <span class="drawer-size">{d.get_size_display || d.size}</span>
                                </div>
                                <div class="drawer-capacity">
                                    Capacidad: {d.current_capacity || 0}/{d.max_capacity}
                                </div>
                            </div>
                        {/each}
                    </div>
                {/if}
            </div>
        {:else}
            <div class="no-selection">
                <p>Selecciona un armario para ver y gestionar sus cajones</p>
            </div>
        {/if}
    </div>
    <div class="dashboard-right">
        <h3>Objetos</h3>
        <form onsubmit={createObject} class="create-form">
            <div class="form-group">
                <label for="objectName">Nombre del objeto</label>
                <input id="objectName" type="text" bind:value={objectName} required placeholder="Ej: Camiseta Blanca Premium" />
            </div>
            <div class="form-group">
                <label for="objectType">Tipo</label>
                <select id="objectType" bind:value={objectType} required>
                    <option value="" disabled selected>Selecciona un tipo</option>
                    {#each typeOptions as opt}
                        <option value={opt.value}>{opt.label}</option>
                    {/each}
                </select>
            </div>
            <div class="form-group">
                <label for="objectSize">Tamaño</label>
                <select id="objectSize" bind:value={objectSize} required>
                    <option value="" disabled selected>Selecciona un tamaño</option>
                    {#each sizeOptions as opt}
                        <option value={opt.value}>{opt.label}</option>
                    {/each}
                </select>
            </div>
            <button type="submit" disabled={objectLoading}>{objectLoading ? 'Creando...' : 'Crear objeto'}</button>
            {#if objectError}
                <div class="error">{objectError}</div>
            {/if}
            {#if objectSuccess}
                <div class="success">{objectSuccess}</div>
            {/if}
        </form>
        
        <div class="objects-list">
            <div class="objects-header">
                <h4>Objetos disponibles (Total: {objects.length})</h4>
                <button type="button" class="reload-btn" onclick={fetchObjects}>🔄 Recargar</button>
            </div>
            {#if objects.length === 0}
                <div class="empty-list">No hay objetos registrados.</div>
            {:else}
                <div class="objects-grid">
                    {#each objects as obj}
                        <div class="object-card">
                            <div class="object-header">
                                <span class="object-icon">📦</span>
                                <strong>{obj.name}</strong>
                            </div>
                            <div class="object-details">
                                <span class="object-type">{obj.get_type_display || obj.type}</span>
                                <span class="object-size">{obj.get_size_display || obj.size}</span>
                            </div>
                            <div class="object-status">
                                {#if obj.drawer}
                                    <span class="assigned">📍 Asignado a cajón</span>
                                {:else}
                                    <span class="free">🆓 Libre</span>
                                {/if}
                            </div>
                        </div>
                    {/each}
                </div>
            {/if}
        </div>
    </div>
</div>

<style>
.dashboard-container {
    color: black;
    display: flex;
    gap: 2rem;
    align-items: flex-start;
    justify-content: center;
    margin: 2rem auto;
    max-width: 1200px;
}
.dashboard-left, .dashboard-center, .dashboard-right {
    background: #fff;
    border-radius: 1rem;
    box-shadow: 0 2px 16px #0001;
    padding: 2rem 1.5rem;
    min-width: 320px;
    flex: 1 1 0;
}
.dashboard-left {
    max-width: 300px;
}
.dashboard-center {
    max-width: 350px;
}
.dashboard-right {
    max-width: 350px;
}
.create-form {
    display: flex;
    flex-direction: column;
    gap: 1.2rem;
    margin-bottom: 1.5rem;
}
.form-group {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
}
label {
    font-weight: 600;
    margin-bottom: 0.3rem;
}
input, select {
    width: 100%;
    padding: 0.5rem 0.7rem;
    border-radius: 0.5rem;
    border: 1px solid #ddd;
    font-size: 1rem;
}
button {
    background: linear-gradient(90deg, #38bdf8, #6366f1);
    color: #fff;
    border: none;
    border-radius: 0.5rem;
    padding: 0.7rem 1.2rem;
    font-size: 1.1rem;
    font-weight: 700;
    cursor: pointer;
    transition: background 0.2s;
}
button:disabled {
    opacity: 0.7;
    cursor: not-allowed;
}
.closets-list ul {
    padding-left: 1.2rem;
    margin: 0;
}
.closets-list li {
    cursor: pointer;
    padding: 0.2rem 0.5rem;
    border-radius: 0.3rem;
    margin-bottom: 0.2rem;
}
.closets-list li.selected {
    background: #e0e7ff;
    font-weight: bold;
}
.error {
    color: #ef4444;
    margin-top: 0.5rem;
}
.success {
    color: #10b981;
    margin-top: 0.5rem;
}
.empty-list {
    color: #888;
    font-size: 0.95rem;
    margin: 0.5rem 0 1rem 0;
}
.selected-closet-info {
    background: #f0f9ff;
    border: 1px solid #0ea5e9;
    border-radius: 0.5rem;
    padding: 1rem;
    margin-bottom: 1.5rem;
}
.selected-closet-info h4 {
    margin: 0 0 0.5rem 0;
    color: #0369a1;
}
.closet-details {
    margin: 0;
    color: #0891b2;
    font-size: 0.9rem;
}
.no-selection {
    text-align: center;
    color: #888;
    padding: 2rem;
    background: #f9fafb;
    border-radius: 0.5rem;
    border: 1px dashed #d1d5db;
}
.drawers-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
}
.drawer-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 0.5rem;
    padding: 1rem;
    transition: all 0.2s;
}
.drawer-card:hover {
    background: #f1f5f9;
    border-color: #cbd5e1;
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
.drawer-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
}
.drawer-icon {
    font-size: 1.2rem;
}
.drawer-details {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
}
.drawer-type, .drawer-size {
    background: #e0e7ff;
    color: #4338ca;
    padding: 0.2rem 0.5rem;
    border-radius: 0.25rem;
    font-size: 0.75rem;
    font-weight: 600;
}
.drawer-capacity {
    font-size: 0.8rem;
    color: #64748b;
    font-weight: 500;
}
.closets-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
}
.closets-header h4 {
    margin: 0;
}
.reload-btn {
    background: #10b981;
    color: white;
    border: none;
    border-radius: 0.375rem;
    padding: 0.375rem 0.75rem;
    font-size: 0.875rem;
    cursor: pointer;
    transition: background 0.2s;
}
.reload-btn:hover {
    background: #059669;
}

.objects-list {
    margin-top: 1.5rem;
}

.objects-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
}

.objects-header h4 {
    margin: 0;
}

.objects-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
}

.object-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 0.5rem;
    padding: 1rem;
    transition: all 0.2s;
}

.object-card:hover {
    background: #f1f5f9;
    border-color: #cbd5e1;
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.object-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
}

.object-icon {
    font-size: 1.2rem;
}

.object-details {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
}

.object-type, .object-size {
    background: #e0e7ff;
    color: #4338ca;
    padding: 0.2rem 0.5rem;
    border-radius: 0.25rem;
    font-size: 0.75rem;
    font-weight: 600;
}

.object-status {
    font-size: 0.8rem;
    font-weight: 500;
}

.assigned {
    color: #059669;
}

.free {
    color: #0891b2;
}

/* Header styles */
.page-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1.5rem 2rem;
    margin-bottom: 2rem;
    border-radius: 1rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    max-width: 1200px;
    margin: 0 auto;
}

.page-header h1 {
    margin: 0;
    font-size: 2rem;
    font-weight: 700;
    color: white;
}

.header-nav {
    display: flex;
    gap: 1rem;
}

.nav-link {
    background: rgba(255, 255, 255, 0.2);
    color: white;
    text-decoration: none;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 0.5rem;
    font-weight: 600;
    font-size: 1rem;
    transition: all 0.3s ease;
    border: 2px solid transparent;
    backdrop-filter: blur(10px);
    cursor: pointer;
    font-family: inherit;
}

.nav-link:hover {
    background: rgba(255, 255, 255, 0.3);
    border-color: rgba(255, 255, 255, 0.5);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

@media (max-width: 768px) {
    .header-content {
        flex-direction: column;
        gap: 1rem;
        text-align: center;
    }
    
    .page-header h1 {
        font-size: 1.5rem;
    }
    
    .nav-link {
        padding: 0.6rem 1.2rem;
        font-size: 0.9rem;
    }
}
</style>
