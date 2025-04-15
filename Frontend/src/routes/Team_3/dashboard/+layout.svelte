<script>
  import Sidebar from '$lib/components/Sidebar.svelte';
  import { page } from '$app/stores';
  import '../../Styling/app.css';
  
  // Extract the current section from the URL
  $: currentSection = $page.url.pathname.split('/').pop() || 'projects';
</script>

<div class="dashboard-layout">
  <Sidebar activeSection={currentSection} />
  
  <main class="content">
    <slot />
  </main>
</div>

<style>
  .dashboard-layout {
    display: flex;
    width: 100%;
    height: 100vh;
    overflow: hidden;
  }
  
  .content {
    flex: 1;
    padding: 20px;
    overflow-y: auto;
  }
  
  :global(body) {
    margin: 0;
    padding: 0;
    font-family: Arial, sans-serif;
  }
</style>