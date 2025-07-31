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

    <section class="closet-section">
        <Closet closetData={mockCloset} />
    </section>
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
        max-width: 1400px;
        margin: 0 auto;
        background: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
        padding: 2rem;
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

        .closet-section {
            padding: 1rem;
        }

        .nav-link {
            padding: 0.6rem 1.2rem;
            font-size: 0.9rem;
        }
    }
</style>
