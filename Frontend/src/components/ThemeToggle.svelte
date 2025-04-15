<script>
  import { darkMode } from '$lib/stores/theme.js';
  
  function toggleDarkMode() {
    $darkMode = !$darkMode;
  }
</script>

<button 
  class="theme-toggle" 
  title="Toggle dark mode"
  on:click={toggleDarkMode}
>
  {$darkMode ? '☀️' : '🌙'}
</button>

<style>
  .theme-toggle {
    background: none;
    border: none;
    font-size: 18px;
    cursor: pointer;
    padding: 5px 10px;
    color: inherit;
  }
</style>