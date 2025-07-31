<script>
    let { closetData } = $props();
    
    // Estado de la aplicación
    let selectedDrawer = $state(null);
    let openDrawers = $state(new Set());

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
        if (openDrawers.has(drawer.id)) {
            openDrawers.delete(drawer.id);
            if (selectedDrawer?.id === drawer.id) {
                selectedDrawer = null;
            }
        } else {
            openDrawers.add(drawer.id);
            selectedDrawer = drawer;
        }
        openDrawers = new Set(openDrawers); // Forzar reactividad
    }
</script>

<div class="container">
    <div class="title">
        <h1>🪵 {closetData.name} 🪵</h1>
        <div class="title-line"></div>
    </div>

    <div class="main-layout">
        <div class="closet-frame">
            <div class="wood-grain"></div>
            
            <div class="closet-interior">
                <div class="interior-grain"></div>
                
                <div class="drawers-container">
                    {#each closetData.drawers as drawer, index}
                        {@const occupancy = getOccupancyPercentage(drawer)}
                        {@const isOpen = openDrawers.has(drawer.id)}
                        
                        <div 
                            class="drawer {sizeClasses[drawer.size]} {isOpen ? 'open' : ''}"
                            data-drawer-id={drawer.id}
                            onclick={() => handleDrawerClick(drawer)}
                            role="button"
                            tabindex="0"
                            onkeydown={(e) => e.key === 'Enter' && handleDrawerClick(drawer)}
                        >
                            <div class="drawer-shadow"></div>
                            <div 
                                class="drawer-face" 
                                style="background: {typeColors[drawer.type]}, {woodPatterns[index % woodPatterns.length]};"
                            >
                                <div class="drawer-content">
                                    <div class="drawer-left">
                                        <div class="drawer-icon">{typeIcons[drawer.type]}</div>
                                        <div class="drawer-info">
                                            <h3>{drawer.name}</h3>
                                            <div class="type">{drawer.get_type_display}</div>
                                        </div>
                                    </div>
                                    
                                    <div class="capacity-bar">
                                        <div 
                                            class="capacity-fill {getCapacityClass(occupancy)}" 
                                            style="width: {occupancy}%"
                                        ></div>
                                    </div>
                                    
                                    <div class="drawer-stats">
                                        <div class="count" style="color: {getCapacityColor(occupancy)}">
                                            {drawer.stored_objects?.length || 0}/{drawer.max_capacity}
                                        </div>
                                        <div class="size">{drawer.size}</div>
                                    </div>
                                    
                                    <div class="drawer-handle"></div>
                                </div>
                            </div>
                        </div>
                    {/each}
                </div>
            </div>
        </div>

        <!-- Panel de Detalles -->
        {#if selectedDrawer}
            {@const occupancy = getOccupancyPercentage(selectedDrawer)}
            <div class="details-panel">
                <div class="details-header">
                    <div class="details-icon">{typeIcons[selectedDrawer.type]}</div>
                    <h3 class="details-title">{selectedDrawer.name}</h3>
                    <div class="details-type">{selectedDrawer.get_type_display} • {selectedDrawer.get_size_display}</div>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number" style="color: {getCapacityColor(occupancy)}">
                            {selectedDrawer.stored_objects?.length || 0}
                        </div>
                        <div class="stat-label">Objetos</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{selectedDrawer.max_capacity}</div>
                        <div class="stat-label">Capacidad</div>
                    </div>
                </div>
                
                {#if selectedDrawer.stored_objects?.length > 0}
                    <div class="objects-section">
                        <h4 class="section-title">📦 Contenido</h4>
                        <div class="objects-list">
                            {#each selectedDrawer.stored_objects as object, index}
                                <div class="object-item" style="animation-delay: {index * 0.1}s">
                                    <div class="object-name">
                                        <div class="object-dot"></div>
                                        {object.name}
                                    </div>
                                    <div class="object-size">Tamaño: {object.size}</div>
                                </div>
                            {/each}
                        </div>
                    </div>
                {:else}
                    <div class="empty-state">
                        <div class="empty-icon">📭</div>
                        <p><strong>Cajón vacío</strong></p>
                        <p>¡Perfecto para guardar cosas nuevas!</p>
                    </div>
                {/if}
            </div>
        {/if}
    </div>

    <!-- Instrucciones -->
    {#if !selectedDrawer}
        <div class="instructions">
            <p>🖱️ <span class="highlight">¡Haz clic en cualquier cajón para abrirlo y descubrir sus secretos!</span></p>
        </div>
    {/if}
</div>

<style>
    .container {
        max-width: 1400px;
        margin: 0 auto;
    }

    .title {
        text-align: center;
        margin-bottom: 40px;
    }

    .title h1 {
        font-size: 3.5rem;
        color: #92400E;
        text-shadow: 3px 3px 0px #8B4513, -1px -1px 0px #D2691E;
        margin-bottom: 10px;
        animation: titleGlow 3s ease-in-out infinite alternate;
    }

    @keyframes titleGlow {
        0% { text-shadow: 3px 3px 0px #8B4513, -1px -1px 0px #D2691E; }
        100% { text-shadow: 3px 3px 10px #8B4513, -1px -1px 10px #D2691E; }
    }

    .title-line {
        width: 200px;
        height: 4px;
        background: linear-gradient(to right, #92400E, #D97706, #92400E);
        margin: 0 auto;
        border-radius: 2px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }

    .main-layout {
        display: grid;
        grid-template-columns: 2fr 1fr;
        gap: 40px;
        align-items: start;
    }

    .closet-frame {
        background: linear-gradient(145deg, #8B4513, #A0522D, #654321);
        border-radius: 30px;
        padding: 30px;
        box-shadow: 
            0 20px 40px rgba(0,0,0,0.3),
            inset 0 2px 4px rgba(255,255,255,0.2),
            inset 0 -2px 4px rgba(0,0,0,0.2);
        position: relative;
        overflow: hidden;
    }

    .closet-frame::before,
    .closet-frame::after {
        content: '';
        position: absolute;
        width: 40px;
        height: 40px;
        background: radial-gradient(circle, #D4AF37, #B8860B);
        border-radius: 50%;
    }

    .closet-frame::before {
        top: 20px;
        left: 20px;
        box-shadow: inset 2px 2px 4px rgba(0,0,0,0.3);
    }

    .closet-frame::after {
        top: 20px;
        right: 20px;
        box-shadow: inset 2px 2px 4px rgba(0,0,0,0.3);
    }

    .wood-grain {
        position: absolute;
        inset: 0;
        background-image: 
            repeating-linear-gradient(45deg, 
                transparent, transparent 2px, 
                rgba(255,255,255,0.1) 2px, 
                rgba(255,255,255,0.1) 4px),
            repeating-linear-gradient(0deg,
                transparent, transparent 15px,
                rgba(139,69,19,0.3) 15px,
                rgba(139,69,19,0.3) 17px);
        border-radius: 25px;
        opacity: 0.7;
    }

    .closet-interior {
        background: linear-gradient(135deg, #F4E4BC, #E6D3A3, #D4B896);
        border-radius: 20px;
        padding: 25px;
        position: relative;
        box-shadow: 
            inset 0 0 20px rgba(0,0,0,0.1),
            inset 0 2px 4px rgba(255,255,255,0.3);
    }

    .interior-grain {
        position: absolute;
        inset: 0;
        background-image: 
            repeating-linear-gradient(90deg,
                transparent, transparent 10px,
                rgba(160,82,45,0.1) 10px,
                rgba(160,82,45,0.1) 11px);
        border-radius: 15px;
    }

    .drawers-container {
        display: flex;
        flex-direction: column;
        gap: 15px;
        position: relative;
        z-index: 1;
    }

    .drawer {
        background: white;
        border-radius: 15px;
        box-shadow: 
            0 8px 16px rgba(0,0,0,0.15),
            inset 0 1px 2px rgba(255,255,255,0.5);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }

    .drawer:hover {
        transform: translateY(-3px);
        box-shadow: 
            0 12px 24px rgba(0,0,0,0.2),
            inset 0 1px 2px rgba(255,255,255,0.5);
    }

    .drawer.open {
        transform: translateX(20px) scale(1.02);
        box-shadow: 
            0 15px 30px rgba(0,0,0,0.25),
            inset 0 1px 2px rgba(255,255,255,0.5);
        z-index: 10;
    }

    .drawer-shadow {
        position: absolute;
        inset: 0;
        background: linear-gradient(145deg, rgba(0,0,0,0.1), transparent 60%);
        pointer-events: none;
        border-radius: 15px;
    }

    .drawer-face {
        border-radius: 15px;
        position: relative;
        overflow: hidden;
    }

    .drawer-content {
        display: flex;
        align-items: center;
        padding: 0 20px;
        height: 80px;
        position: relative;
        z-index: 1;
    }

    .drawer-small .drawer-content { height: 70px; }
    .drawer-medium .drawer-content { height: 80px; }
    .drawer-large .drawer-content { height: 90px; }

    .drawer-left {
        display: flex;
        align-items: center;
        gap: 15px;
        flex: 1;
    }

    .drawer-icon {
        font-size: 2rem;
        filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.3));
    }

    .drawer-info h3 {
        font-size: 1.3rem;
        color: #1F2937;
        margin-bottom: 5px;
        font-weight: 700;
        text-shadow: 1px 1px 2px rgba(255,255,255,0.5);
    }

    .drawer-info .type {
        font-size: 0.9rem;
        color: #6B7280;
        font-weight: 500;
        opacity: 0.9;
    }

    .capacity-bar {
        flex: 1;
        height: 8px;
        background: rgba(255,255,255,0.3);
        border-radius: 4px;
        margin: 0 20px;
        overflow: hidden;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.2);
    }

    .capacity-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 0.6s ease-out;
        position: relative;
        overflow: hidden;
    }

    .capacity-fill::after {
        content: '';
        position: absolute;
        inset: 0;
        background: linear-gradient(45deg,
            rgba(255,255,255,0.3) 25%,
            transparent 25%,
            transparent 50%,
            rgba(255,255,255,0.3) 50%,
            rgba(255,255,255,0.3) 75%,
            transparent 75%);
        background-size: 8px 8px;
        animation: barberpole 1s linear infinite;
    }

    @keyframes barberpole {
        0% { background-position: 0 0; }
        100% { background-position: 8px 0; }
    }

    .capacity-low {
        background: linear-gradient(135deg, #10B981, #059669);
    }

    .capacity-medium {
        background: linear-gradient(135deg, #F59E0B, #D97706);
    }

    .capacity-high {
        background: linear-gradient(135deg, #EF4444, #DC2626);
    }

    .drawer-stats {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 3px;
    }

    .drawer-stats .count {
        font-size: 1.1rem;
        font-weight: 700;
        text-shadow: 1px 1px 2px rgba(255,255,255,0.5);
    }

    .drawer-stats .size {
        font-size: 0.8rem;
        color: #6B7280;
        font-weight: 600;
        background: rgba(255,255,255,0.6);
        padding: 2px 8px;
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.3);
    }

    .drawer-handle {
        width: 6px;
        height: 40px;
        background: linear-gradient(145deg, #D4AF37, #B8860B);
        border-radius: 3px;
        margin-left: 15px;
        box-shadow: 
            0 2px 6px rgba(0,0,0,0.3),
            inset 0 1px 2px rgba(255,255,255,0.4);
        position: relative;
    }

    .drawer-handle::before {
        content: '';
        position: absolute;
        width: 8px;
        height: 8px;
        background: radial-gradient(circle, #F7DC6F, #D4AF37);
        border-radius: 50%;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        box-shadow: inset 0 1px 2px rgba(0,0,0,0.2);
    }

    .details-panel {
        background: white;
        border-radius: 20px;
        padding: 30px;
        box-shadow: 
            0 10px 30px rgba(0,0,0,0.1),
            inset 0 1px 3px rgba(255,255,255,0.5);
        position: sticky;
        top: 20px;
        animation: slideInRight 0.5s ease-out;
    }

    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    .details-header {
        text-align: center;
        margin-bottom: 25px;
        padding-bottom: 20px;
        border-bottom: 2px solid #F3F4F6;
    }

    .details-icon {
        font-size: 3rem;
        margin-bottom: 10px;
        filter: drop-shadow(3px 3px 6px rgba(0,0,0,0.2));
    }

    .details-title {
        font-size: 1.8rem;
        color: #1F2937;
        margin-bottom: 8px;
        font-weight: 700;
    }

    .details-type {
        font-size: 1rem;
        color: #6B7280;
        font-weight: 500;
    }

    .stats-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 15px;
        margin-bottom: 25px;
    }

    .stat-card {
        background: linear-gradient(135deg, #F8FAFC, #E2E8F0);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 
            0 4px 12px rgba(0,0,0,0.05),
            inset 0 1px 2px rgba(255,255,255,0.5);
    }

    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .stat-label {
        font-size: 0.9rem;
        color: #6B7280;
        font-weight: 500;
    }

    .objects-section {
        margin-top: 20px;
    }

    .section-title {
        font-size: 1.3rem;
        color: #1F2937;
        margin-bottom: 15px;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .objects-list {
        display: flex;
        flex-direction: column;
        gap: 10px;
    }

    .object-item {
        background: linear-gradient(135deg, #FEFCE8, #FEF3C7);
        border-radius: 10px;
        padding: 15px;
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

    .object-name {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 1rem;
        font-weight: 600;
        color: #92400E;
        margin-bottom: 5px;
    }

    .object-dot {
        width: 6px;
        height: 6px;
        background: #F59E0B;
        border-radius: 50%;
        flex-shrink: 0;
    }

    .object-size {
        font-size: 0.85rem;
        color: #78716C;
        font-weight: 500;
    }

    .empty-state {
        text-align: center;
        padding: 40px 20px;
        color: #6B7280;
    }

    .empty-icon {
        font-size: 3rem;
        margin-bottom: 15px;
        opacity: 0.7;
    }

    .empty-state p {
        margin-bottom: 8px;
    }

    .instructions {
        text-align: center;
        margin-top: 30px;
        padding: 20px;
        background: rgba(255,255,255,0.9);
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }

    .instructions p {
        font-size: 1.2rem;
        color: #6B7280;
    }

    .instructions .highlight {
        font-weight: bold;
        color: #1F2937;
    }

    @media (max-width: 1024px) {
        .main-layout {
            grid-template-columns: 1fr;
            gap: 30px;
        }
        
        .title h1 {
            font-size: 2.5rem;
        }
    }

    @media (max-width: 768px) {
        .closet-frame {
            padding: 20px;
        }
        
        .drawer-content {
            padding: 0 15px;
        }
        
        .capacity-bar {
            margin: 0 10px;
        }
    }
</style>