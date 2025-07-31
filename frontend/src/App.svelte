<script lang="ts">
  import Homepage from './lib/create.svelte';
</script>

<main>
  <Homepage />
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
