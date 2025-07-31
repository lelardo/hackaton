<script>
import { onMount } from 'svelte';
// Paso 1: Closet
let closetName = '';
let closetSuccess = '';
let closetError = '';
let closetLoading = false;
let closetId = null;

// Paso 2: Cajones
let drawers = [];
let drawerName = '';
let drawerType = '';
let drawerSize = '';
let drawerCapacity = '';
let drawerError = '';
let drawerSuccess = '';
let drawerLoading = false;

// Paso 3: Objetos
let objects = [];
let objectName = '';
let objectType = '';
let objectSize = '';
let objectDrawer = '';
let objectError = '';
let objectSuccess = '';
let objectLoading = false;

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

// Crear closet
async function createCloset() {
    closetError = '';
    closetSuccess = '';
    closetLoading = true;
    try {
        const res = await fetch('/app/closets/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: closetName })
        });
        if (!res.ok) {
            const data = await res.json();
            throw new Error(data.error || 'Error al crear el closet');
        }
        const data = await res.json();
        closetId = data.id;
        closetSuccess = '¡Closet creado exitosamente! Ahora agrega cajones.';
        closetName = '';
    } catch (e) {
        closetError = e.message;
    }
    closetLoading = false;
}

// Crear cajón
async function createDrawer() {
    drawerError = '';
    drawerSuccess = '';
    drawerLoading = true;
    try {
        const res = await fetch('/app/drawers/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: drawerName,
                type: drawerType,
                size: drawerSize,
                max_capacity: drawerCapacity,
                closet: closetId
            })
        });
        if (!res.ok) {
            const data = await res.json();
            throw new Error(data.error || 'Error al crear el cajón');
        }
        const data = await res.json();
        drawers = [...drawers, data];
        drawerSuccess = '¡Cajón agregado! Puedes agregar más o pasar al siguiente paso.';
        drawerName = '';
        drawerType = '';
        drawerSize = '';
        drawerCapacity = '';
    } catch (e) {
        drawerError = e.message;
    }
    drawerLoading = false;
}

// Crear objeto y asignar a cajón
async function createObject() {
    objectError = '';
    objectSuccess = '';
    objectLoading = true;
    try {
        // 1. Crear objeto
        const res = await fetch('/app/objects/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: objectName, type: objectType, size: objectSize })
        });
        if (!res.ok) {
            const data = await res.json();
            throw new Error(data.error || 'Error al crear el objeto');
        }
        const obj = await res.json();
        // 2. Asignar objeto al cajón
        const assignRes = await fetch(`/app/drawers/${objectDrawer}/assign-object/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ object_id: obj.id })
        });
        if (!assignRes.ok) {
            const data = await assignRes.json();
            throw new Error(data.error || 'Error al asignar el objeto al cajón');
        }
        objects = [...objects, obj];
        objectSuccess = '¡Objeto creado y asignado exitosamente!';
        objectName = '';
        objectType = '';
        objectSize = '';
        objectDrawer = '';
    } catch (e) {
        objectError = e.message;
    }
    objectLoading = false;
}
</script>

<div class="create-container">
    <h2>Wizard de Catálogo: Closet, Cajones y Objetos</h2>
    <!-- Paso 1: Closet -->
    {#if !closetId}
        <form on:submit|preventDefault={createCloset} class="create-form">
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
    {/if}

    <!-- Paso 2: Cajones -->
    {#if closetId}
        <div class="step-section">
            <h3>Agregar cajones al closet</h3>
            <form on:submit|preventDefault={createDrawer} class="create-form">
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
            {#if drawers.length > 0}
                <div class="drawers-list">
                    <h4>Cajones agregados:</h4>
                    <ul>
                        {#each drawers as d}
                            <li>{d.name} ({d.get_type_display || d.type}, {d.get_size_display || d.size}) - Capacidad: {d.max_capacity}</li>
                        {/each}
                    </ul>
                </div>
            {/if}
        </div>
    {/if}

    <!-- Paso 3: Objetos -->
    {#if closetId && drawers.length > 0}
        <div class="step-section">
            <h3>Agregar objetos y asignar a cajones</h3>
            <form on:submit|preventDefault={createObject} class="create-form">
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
                <div class="form-group">
                    <label for="objectDrawer">Asignar a cajón</label>
                    <select id="objectDrawer" bind:value={objectDrawer} required>
                        <option value="" disabled selected>Selecciona un cajón</option>
                        {#each drawers as d}
                            <option value={d.id}>{d.name} ({d.get_type_display || d.type}, {d.get_size_display || d.size})</option>
                        {/each}
                    </select>
                </div>
                <button type="submit" disabled={objectLoading}>{objectLoading ? 'Agregando...' : 'Agregar objeto'}</button>
                {#if objectError}
                    <div class="error">{objectError}</div>
                {/if}
                {#if objectSuccess}
                    <div class="success">{objectSuccess}</div>
                {/if}
            </form>
            {#if objects.length > 0}
                <div class="objects-list">
                    <h4>Objetos agregados:</h4>
                    <ul>
                        {#each objects as o}
                            <li>{o.name} ({o.type}, {o.size})</li>
                        {/each}
                    </ul>
                </div>
            {/if}
        </div>
    {/if}
</div>

<style>


.create-form {
    display: flex;
    flex-direction: column;
    gap: 1.2rem;
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
.error {
    color: #ef4444;
    margin-top: 0.5rem;
}
.success {
    color: #10b981;
    margin-top: 0.5rem;
}
</style>
