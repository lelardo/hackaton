<script>
    import { onMount } from 'svelte';
    import Closet from '../components/closet.svelte';

    // Estado
    let closets = $state([]);
    let selectedCloset = $state(null);
    let recommendations = $state([]);
    let loadingRecommendations = $state(false);

    // Cargar closets al iniciar
    onMount(async () => {
        await fetchClosets();
    });

    async function fetchClosets() {
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
            closets = Array.isArray(data) ? [...data] : [];
            
            // Seleccionar el primer closet por defecto
            if (closets.length > 0) {
                selectedCloset = closets[0];
                await loadRecommendations();
            }
        } catch (e) {
            console.error('Error fetching closets:', e);
            closets = [];
        }
    }

    async function loadRecommendations() {
        if (!selectedCloset || !selectedCloset.drawers || selectedCloset.drawers.length === 0) return;
        
        loadingRecommendations = true;
        recommendations = [];
        
        try {
            // Obtener recomendaciones para cada cajón
            const recommendationPromises = selectedCloset.drawers.map(async (drawer) => {
                try {
                    const res = await fetch(`http://localhost:8000/app/drawers/${drawer.id}/recommendation/`);
                    if (res.ok) {
                        const data = await res.json();
                        return {
                            drawerName: drawer.name,
                            recommendation: data.recommendation
                        };
                    }
                } catch (e) {
                    console.error(`Error getting recommendation for drawer ${drawer.id}:`, e);
                }
                return {
                    drawerName: drawer.name,
                    recommendation: "Organiza este cajón por categorías para mayor eficiencia."
                };
            });

            const results = await Promise.all(recommendationPromises);
            recommendations = results.slice(0, 3); // Solo mostrar las primeras 3
        } catch (e) {
            console.error('Error loading recommendations:', e);
            recommendations = [
                { drawerName: "General", recommendation: "Mantén tus objetos organizados por categorías." }
            ];
        } finally {
            loadingRecommendations = false;
        }
    }

    async function selectCloset(closet) {
        selectedCloset = closet;
        await loadRecommendations();
    }
</script>

<main class="homepage">
    <header>
        <div class="header-content">
            <div class="header-text">
                <h1>Sistema de Gestión de Armarios</h1>
                <p class="subtitle">Organiza tus espacios de manera eficiente</p>
            </div>
            <nav class="header-nav">
                <button 
                    class="nav-link"
                    onclick={() => window.navigate('/create')}
                >
                    ➕ Panel de Creación
                </button>
            </nav>
        </div>
    </header>

    <!-- Selector de Closets -->
    {#if closets.length > 0}
        <section class="closet-selector">
            <h2>📚 Selecciona un Armario</h2>
            <div class="closet-buttons">
                {#each closets as closet}
                    <button 
                        class="closet-btn {selectedCloset?.id === closet.id ? 'active' : ''}"
                        onclick={() => selectCloset(closet)}
                    >
                        🗄️ {closet.name}
                    </button>
                {/each}
            </div>
        </section>
    {/if}

    <div class="main-content">
        <!-- Contenido del closet -->
        <section class="closet-section">
            {#if selectedCloset}
                <Closet closetData={selectedCloset} />
            {:else if closets.length === 0}
                <div class="empty-state">
                    <div class="empty-icon">📭</div>
                    <h3>No hay armarios disponibles</h3>
                    <p>Crea tu primer armario en el panel de creación</p>
                    <button 
                        class="create-btn"
                        onclick={() => window.navigate('/create')}
                    >
                        ➕ Crear Armario
                    </button>
                </div>
            {/if}
        </section>

        <!-- Panel de Recomendaciones -->
        {#if selectedCloset}
            <aside class="recommendations-panel">
                <div class="recommendations-header">
                    <h3>💡 Recomendaciones IA</h3>
                    <button 
                        class="refresh-btn"
                        onclick={loadRecommendations}
                        disabled={loadingRecommendations}
                    >
                        {loadingRecommendations ? '⏳' : '🔄'}
                    </button>
                </div>
                
                <div class="recommendations-content">
                    {#if loadingRecommendations}
                        <div class="loading-recommendations">
                            <div class="spinner"></div>
                            <p>Generando recomendaciones...</p>
                        </div>
                    {:else if recommendations.length > 0}
                        {#each recommendations as rec, index}
                            <div class="recommendation-card" style="animation-delay: {index * 0.1}s">
                                <div class="rec-header">
                                    <span class="rec-icon">📋</span>
                                    <strong>{rec.drawerName}</strong>
                                </div>
                                <p class="rec-text">{rec.recommendation}</p>
                            </div>
                        {/each}
                    {:else}
                        <div class="no-recommendations">
                            <div class="no-rec-icon">🤔</div>
                            <p>No hay recomendaciones disponibles</p>
                        </div>
                    {/if}
                </div>
            </aside>
        {/if}
    </div>
</main>

<style>
    .homepage {
        min-height: 100vh;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2rem;
    }

    header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        margin-bottom: 3rem;
        border-radius: 15px;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
    }

    .header-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        max-width: 1400px;
        margin: 0 auto;
    }

    .header-text {
        flex: 1;
    }

    h1 {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        color: white;
    }

    .subtitle {
        font-size: 1.2rem;
        color: rgba(255, 255, 255, 0.9);
        margin: 0;
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
        white-space: nowrap;
        cursor: pointer;
        font-family: inherit;
    }

    .nav-link:hover {
        background: rgba(255, 255, 255, 0.3);
        border-color: rgba(255, 255, 255, 0.5);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }

    .closet-section {
        flex: 1;
        background: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
        padding: 2rem;
    }

    .closet-selector {
        max-width: 1400px;
        margin: 0 auto 2rem auto;
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }

    .closet-selector h2 {
        margin-bottom: 1rem;
        color: #1F2937;
        font-size: 1.5rem;
        text-align: center;
    }

    .closet-buttons {
        display: flex;
        gap: 1rem;
        justify-content: center;
        flex-wrap: wrap;
    }

    .closet-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 10px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        font-family: inherit;
        font-size: 1rem;
    }

    .closet-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
    }

    .closet-btn.active {
        background: linear-gradient(135deg, #10B981, #059669);
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
    }

    .main-content {
        display: grid;
        grid-template-columns: 1fr 350px;
        gap: 2rem;
        max-width: 1400px;
        margin: 0 auto;
    }

    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
        color: #6B7280;
    }

    .empty-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        opacity: 0.7;
    }

    .empty-state h3 {
        color: #1F2937;
        margin-bottom: 0.5rem;
    }

    .create-btn {
        background: linear-gradient(135deg, #10B981, #059669);
        color: white;
        border: none;
        padding: 1rem 2rem;
        border-radius: 10px;
        font-weight: 600;
        cursor: pointer;
        margin-top: 1rem;
        font-family: inherit;
        font-size: 1.1rem;
        transition: all 0.3s ease;
    }

    .create-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(16, 185, 129, 0.4);
    }

    .recommendations-panel {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
        height: fit-content;
        position: sticky;
        top: 2rem;
    }

    .recommendations-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid #F3F4F6;
    }

    .recommendations-header h3 {
        color: #1F2937;
        margin: 0;
        font-size: 1.3rem;
    }

    .refresh-btn {
        background: linear-gradient(135deg, #F59E0B, #D97706);
        color: white;
        border: none;
        padding: 0.5rem;
        border-radius: 8px;
        cursor: pointer;
        font-size: 1rem;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
    }

    .refresh-btn:hover:not(:disabled) {
        transform: scale(1.1);
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.4);
    }

    .refresh-btn:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }

    .loading-recommendations {
        text-align: center;
        padding: 2rem;
        color: #6B7280;
    }

    .spinner {
        width: 40px;
        height: 40px;
        border: 4px solid #F3F4F6;
        border-top: 4px solid #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 0 auto 1rem;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .recommendation-card {
        background: linear-gradient(135deg, #FEFCE8, #FEF3C7);
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        border-left: 4px solid #F59E0B;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        animation: fadeInUp 0.4s ease-out both;
    }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .rec-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.5rem;
        color: #92400E;
        font-weight: 600;
    }

    .rec-icon {
        font-size: 1.1rem;
    }

    .rec-text {
        color: #78716C;
        margin: 0;
        font-size: 0.9rem;
        line-height: 1.4;
    }

    .no-recommendations {
        text-align: center;
        padding: 2rem;
        color: #6B7280;
    }

    .no-rec-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
        opacity: 0.7;
    }

    @media (max-width: 768px) {
        .homepage {
            padding: 1rem;
        }

        .header-content {
            flex-direction: column;
            gap: 1.5rem;
            text-align: center;
        }

        h1 {
            font-size: 2rem;
        }

        .subtitle {
            font-size: 1rem;
        }

        .main-content {
            grid-template-columns: 1fr;
            gap: 1.5rem;
        }

        .closet-section {
            padding: 1rem;
        }

        .nav-link {
            padding: 0.6rem 1.2rem;
            font-size: 0.9rem;
        }

        .closet-buttons {
            flex-direction: column;
            align-items: center;
        }

        .closet-btn {
            width: 100%;
            max-width: 300px;
        }

        .recommendations-panel {
            position: static;
        }
    }
</style>
