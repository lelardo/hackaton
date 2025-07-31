<script lang="ts">
  import Homepage from './lib/homepage.svelte';
  import Create from './lib/create.svelte';

  // Estado del router
  let currentRoute = $state(window.location.pathname);

  // Función para navegar
  function navigate(path: string) {
    currentRoute = path;
    window.history.pushState({}, '', path);
  }

  // Manejar navegación del navegador (botón atrás/adelante)
  $effect(() => {
    function handlePopState() {
      currentRoute = window.location.pathname;
    }
    
    window.addEventListener('popstate', handlePopState);
    
    return () => {
      window.removeEventListener('popstate', handlePopState);
    };
  });

  // Determinar componente a mostrar
  let CurrentComponent = $derived(() => {
    switch (currentRoute) {
      case '/':
        return Homepage;
      case '/create':
        return Create;
      default:
        return Homepage;
    }
  });

  // Hacer disponible la función navigate globalmente
  if (typeof window !== 'undefined') {
    window.navigate = navigate;
  }
</script>

<main>
  {#if currentRoute === '/create'}
    <Create />
  {:else}
    <Homepage />
  {/if}
</main>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen-Sans, Ubuntu, Cantarell, 'Helvetica Neue', sans-serif;
  }

  :global(*) {
    box-sizing: border-box;
  }

  main {
    width: 100%;
    min-height: 100vh;
  }
</style>
