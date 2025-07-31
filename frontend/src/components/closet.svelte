<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Armario de Madera Épico</title>
    <link rel="stylesheet" href="/src/styles/closet.css">
</head>
<body>
    <div class="container">
        <div class="title">
            <h1>🪵 Armario de Roble Clásico 🪵</h1>
            <div class="title-line"></div>
        </div>

        <div class="main-layout">
            <div class="closet-frame">
                <div class="wood-grain"></div>
                
                <div class="closet-interior">
                    <div class="interior-grain"></div>
                    
                    <div class="drawers-container" id="drawersContainer">
                        <!-- Los cajones se generarán dinámicamente -->
                    </div>
                </div>
            </div>

            <!-- Panel de Detalles -->
            <div id="detailsPanel" class="details-panel" style="display: none;">
                <!-- El contenido se generará dinámicamente -->
            </div>
        </div>

        <!-- Instrucciones -->
        <div class="instructions" id="instructions">
            <p>🖱️ <span class="highlight">¡Haz clic en cualquier cajón para abrirlo y descubrir sus secretos!</span></p>
        </div>
    </div>

    <script>
        // Datos del armario
        const closetData = {
            id: 1,
            name: "Armario de Roble Clásico",
            drawers: [
                {
                    id: 1,
                    name: "Camisetas de Algodón",
                    type: 'C',
                    get_type_display: "Ropa",
                    size: 'L',
                    get_size_display: "Grande",
                    max_capacity: 8,
                    stored_objects: [
                        { id: 1, name: "Camiseta Blanca Premium", size: 1 },
                        { id: 2, name: "Polo Navy Clásico", size: 1 },
                        { id: 3, name: "Hoodie Oversized", size: 2 },
                        { id: 4, name: "Tank Top Deportivo", size: 1 },
                        { id: 5, name: "Camisa de Lino", size: 1 }
                    ]
                },
                {
                    id: 2,
                    name: "Documentos Legales",
                    type: 'P',
                    get_type_display: "Papeles",
                    size: 'M',
                    get_size_display: "Mediano",
                    max_capacity: 12,
                    stored_objects: [
                        { id: 6, name: "Pasaporte Vigente", size: 1 },
                        { id: 7, name: "Título Universitario", size: 2 },
                        { id: 8, name: "Contrato de Trabajo", size: 1 },
                        { id: 9, name: "Póliza de Seguro", size: 2 }
                    ]
                },
                {
                    id: 3,
                    name: "Gadgets Tech",
                    type: 'W',
                    get_type_display: "Cables",
                    size: 'S',
                    get_size_display: "Pequeño",
                    max_capacity: 15,
                    stored_objects: [
                        { id: 10, name: "Cable USB-C Trenzado", size: 1 },
                        { id: 11, name: "Cargador MacBook Pro", size: 3 },
                        { id: 12, name: "Cable HDMI 4K", size: 2 },
                        { id: 13, name: "Hub USB Multifunción", size: 2 }
                    ]
                },
                {
                    id: 4,
                    name: "Pantalones Formales",
                    type: 'C',
                    get_type_display: "Ropa",
                    size: 'L',
                    get_size_display: "Grande",
                    max_capacity: 6,
                    stored_objects: [
                        { id: 14, name: "Jeans Levi's 501", size: 2 },
                        { id: 15, name: "Chinos Beige", size: 2 },
                        { id: 16, name: "Shorts de Mezclilla", size: 1 }
                    ]
                },
                {
                    id: 5,
                    name: "Accesorios Especiales",
                    type: 'P',
                    get_type_display: "Papeles",
                    size: 'M',
                    get_size_display: "Mediano",
                    max_capacity: 8,
                    stored_objects: [
                        { id: 17, name: "Reloj Vintage", size: 1 },
                        { id: 18, name: "Gafas de Sol", size: 1 }
                    ]
                },
                {
                    id: 6,
                    name: "Cajón Misterioso",
                    type: 'W',
                    get_type_display: "Cables",
                    size: 'S',
                    get_size_display: "Pequeño",
                    max_capacity: 5,
                    stored_objects: []
                }
            ]
        };

        // Estado de la aplicación
        let selectedDrawer = null;
        let openDrawers = new Set();

        // Configuraciones
        const typeColors = {
            'C': 'linear-gradient(135deg, #FFF1F2, #FECACA, #FCA5A5)',
            'P': 'linear-gradient(135deg, #EFF6FF, #BFDBFE, #93C5FD)',
            'W': 'linear-gradient(135deg, #ECFDF5, #BBF7D0, #86EFAC)'
        };

        const typeIcons = {
            'C': '👔',
            'P': '📋',
            'W': '⚡'
        };

        const sizeClasses = {
            'S': 'drawer-small',
            'M': 'drawer-medium',
            'L': 'drawer-large'
        };

        const woodPatterns = [
            'repeating-linear-gradient(90deg, #D2691E 0px, #CD853F 2px, #DEB887 4px, #D2691E 6px)',
            'repeating-linear-gradient(90deg, #8B4513 0px, #A0522D 1px, #CD853F 3px, #8B4513 4px)',
            'repeating-linear-gradient(90deg, #A0522D 0px, #D2691E 2px, #F4A460 4px, #A0522D 6px)'
        ];

        // Funciones auxiliares
        function getOccupancyPercentage(drawer) {
            return (drawer.stored_objects?.length || 0) / drawer.max_capacity * 100;
        }

        function getCapacityClass(percentage) {
            if (percentage >= 80) return 'capacity-high';
            if (percentage >= 60) return 'capacity-medium';
            return 'capacity-low';
        }

        function getCapacityColor(percentage) {
            if (percentage >= 80) return '#EF4444';
            if (percentage >= 60) return '#F59E0B';
            return '#10B981';
        }

        // Manejar click en cajón
        function handleDrawerClick(drawer) {
            const drawerElement = document.querySelector(`[data-drawer-id="${drawer.id}"]`);
            
            // Agregar animación de shake
            drawerElement.classList.add('animating');
            setTimeout(() => {
                drawerElement.classList.remove('animating');
            }, 600);

            // Manejar estado de apertura
            if (openDrawers.has(drawer.id)) {
                openDrawers.delete(drawer.id);
                drawerElement.classList.remove('open');
                if (selectedDrawer?.id === drawer.id) {
                    selectedDrawer = null;
                    updateDetailsPanel();
                }
            } else {
                openDrawers.add(drawer.id);
                drawerElement.classList.add('open');
                selectedDrawer = drawer;
                updateDetailsPanel();
            }
        }

        // Renderizar cajones
        function renderDrawers() {
            const container = document.getElementById('drawersContainer');
            container.innerHTML = '';

            closetData.drawers.forEach((drawer, index) => {
                const occupancy = getOccupancyPercentage(drawer);
                
                const drawerElement = document.createElement('div');
                drawerElement.className = `drawer ${sizeClasses[drawer.size]}`;
                drawerElement.setAttribute('data-drawer-id', drawer.id);
                
                drawerElement.innerHTML = `
                    <div class="drawer-shadow"></div>
                    <div class="drawer-face" style="background: ${typeColors[drawer.type]}, ${woodPatterns[index % woodPatterns.length]};">
                        <div class="drawer-content">
                            <div class="drawer-left">
                                <div class="drawer-icon">${typeIcons[drawer.type]}</div>
                                <div class="drawer-info">
                                    <h3>${drawer.name}</h3>
                                    <div class="type">${drawer.get_type_display}</div>
                                </div>
                            </div>
                            
                            <div class="capacity-bar">
                                <div class="capacity-fill ${getCapacityClass(occupancy)}" 
                                     style="width: ${occupancy}%"></div>
                            </div>
                            
                            <div class="drawer-stats">
                                <div class="count" style="color: ${getCapacityColor(occupancy)}">
                                    ${drawer.stored_objects?.length || 0}/${drawer.max_capacity}
                                </div>
                                <div class="size">${drawer.size}</div>
                            </div>
                            
                            <div class="drawer-handle"></div>
                        </div>
                    </div>
                `;
                
                drawerElement.addEventListener('click', () => handleDrawerClick(drawer));
                container.appendChild(drawerElement);
            });
        }

        // Actualizar panel de detalles
        function updateDetailsPanel() {
            const panel = document.getElementById('detailsPanel');
            const instructions = document.getElementById('instructions');
            
            if (!selectedDrawer) {
                panel.style.display = 'none';
                instructions.style.display = 'block';
                return;
            }
            
            instructions.style.display = 'none';
            panel.style.display = 'block';
            
            const occupancy = getOccupancyPercentage(selectedDrawer);
            
            panel.innerHTML = `
                <div class="details-header">
                    <div class="details-icon">${typeIcons[selectedDrawer.type]}</div>
                    <h3 class="details-title">${selectedDrawer.name}</h3>
                    <div class="details-type">${selectedDrawer.get_type_display} • ${selectedDrawer.get_size_display}</div>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number" style="color: ${getCapacityColor(occupancy)}">
                            ${selectedDrawer.stored_objects?.length || 0}
                        </div>
                        <div class="stat-label">Objetos</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${selectedDrawer.max_capacity}</div>
                        <div class="stat-label">Capacidad</div>
                    </div>
                </div>
                
                ${selectedDrawer.stored_objects?.length > 0 ? `
                    <div class="objects-section">
                        <h4 class="section-title">📦 Contenido</h4>
                        <div class="objects-list">
                            ${selectedDrawer.stored_objects.map((object, index) => `
                                <div class="object-item" style="animation-delay: ${index * 0.1}s">
                                    <div class="object-name">
                                        <div class="object-dot"></div>
                                        ${object.name}
                                    </div>
                                    <div class="object-size">Tamaño: ${object.size}</div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : `
                    <div class="empty-state">
                        <div class="empty-icon">📭</div>
                        <p><strong>Cajón vacío</strong></p>
                        <p>¡Perfecto para guardar cosas nuevas!</p>
                    </div>
                `}
            `;
        }

        // Inicializar la aplicación
        function init() {
            renderDrawers();
            updateDetailsPanel();
            
            // Agregar efecto de carga
            document.body.style.opacity = '0';
            document.body.style.transform = 'scale(0.95)';
            
            setTimeout(() => {
                document.body.style.transition = 'all 0.8s ease-out';
                document.body.style.opacity = '1';
                document.body.style.transform = 'scale(1)';
            }, 100);
        }

        // Inicializar cuando el DOM esté listo
        document.addEventListener('DOMContentLoaded', init);
    </script>
</body>
</html>