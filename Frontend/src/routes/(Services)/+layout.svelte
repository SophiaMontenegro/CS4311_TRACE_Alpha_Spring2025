<script>
  import Sidebar from "$lib/components/ui/sidebar/Sidebar.svelte";
  import { Toaster } from "$lib/components/ui/sonner/index.js";
  import { ModeWatcher } from "mode-watcher";
  import "../../app.css";
</script>
<svelte:head>
  <title>TRACE | Tool Dashboard</title>
</svelte:head>

<ModeWatcher />

<div class="app-container">
  <Sidebar />
  <main class="content">
    <Toaster />
    <slot />
  </main>
</div>

<style>
  .app-container {
    display: flex;
    max-height: 100vh;
    background-color: var(--background);
  }

  .content {
    flex-grow: 1;
    overflow-y: auto;
  }
</style>
