<script>
    import Closet from '../components/closet.svelte';

    // Datos de ejemplo para el armario
    const mockCloset = {
        id: 1,
        name: "Mi Armario Principal",
        drawers: [
            {
                id: 1,
                name: "Cajón de Ropa",
                type: "C",
                get_type_display: "Clothes",
                size: "L",
                get_size_display: "Large",
                max_capacity: 10,
                stored_objects: [
                    { id: 1, name: "Camisa Azul", size: 1.5 },
                    { id: 2, name: "Pantalón Negro", size: 2.0 },
                    { id: 3, name: "Suéter", size: 1.8 }
                ]
            },
            {
                id: 2,
                name: "Cajón de Documentos",
                type: "P",
                get_type_display: "Papers",
                size: "M",
                get_size_display: "Medium",
                max_capacity: 15,
                stored_objects: [
                    { id: 4, name: "Facturas 2023", size: 0.5 },
                    { id: 5, name: "Contratos", size: 1.0 }
                ]
            },
            {
                id: 3,
                name: "Cajón de Cables",
                type: "W",
                get_type_display: "Wires",
                size: "S",
                get_size_display: "Small",
                max_capacity: 5,
                stored_objects: [
                    { id: 6, name: "Cable USB", size: 0.3 },
                    { id: 7, name: "Cargador Laptop", size: 0.8 },
                    { id: 8, name: "Cable HDMI", size: 0.4 }
                ]
            }
        ]
    };
</script>

<main class="homepage">
    <header>
        <h1>Sistema de Gestión de Armarios</h1>
        <p class="subtitle">Organiza tus espacios de manera eficiente</p>
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
        text-align: center;
        margin-bottom: 3rem;
        color: #2c3e50;
    }

    h1 {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }

    .subtitle {
        font-size: 1.2rem;
        color: #34495e;
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

        h1 {
            font-size: 2rem;
        }

        .subtitle {
            font-size: 1rem;
        }

        .closet-section {
            padding: 1rem;
        }
    }
</style>
