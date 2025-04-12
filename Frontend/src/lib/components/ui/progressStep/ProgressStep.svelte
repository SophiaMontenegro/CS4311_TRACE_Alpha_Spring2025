<script>
  import { onMount } from "svelte";
  import { mode } from "mode-watcher";

  export let status = "config";
</script>

<div class="step-indicator">
  {#if $mode === 'dark'}
  <img
    src="/icons/{status}Dark.svg"
    alt="{status} step" class="svg-icon"

  />
{:else}
  <img
    src="/icons/{status}Light.svg"
    alt="{status} step" class="svg-icon"
  />
{/if}
</div>

<style>
  .step-indicator {
    display: flex;
    justify-content: center;
    align-items: center;
    padding-top: 1rem;
  }

  .svg-icon {
    max-width: 23rem;
    height: 8rem;
  }
</style>