<script>
  import { onMount } from 'svelte';
  import { mode, toggleMode } from 'mode-watcher';
  import Button from '$lib/components/ui/button/button.svelte';
  import { Switch } from '$lib/components/ui/switch/index.js';

  export let isOpen = false;
  export let onClose = () => {
    isOpen = false;
  };

  function handleBackdropClick(event) {
    if (event.target === event.currentTarget) onClose();
  }

  function handleKeydown(event) {
    if (event.key === 'Escape') onClose();
  }

  // reactive dark mode boolean bound to the Switch
  let isDark = false;

  // Sync from mode store
  $: isDark = $mode === 'dark';

  // React to user toggling the switch
  $: if ($mode === 'light' && isDark) toggleMode();
  $: if ($mode === 'dark' && !isDark) toggleMode();
</script>

<svelte:window on:keydown={handleKeydown} />

{#if isOpen}
<div
  class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
  role="button"
  tabindex="0"
  on:click={handleBackdropClick}
  on:keydown={(e) => e.key === 'Enter' && handleBackdropClick(e)}
>

    <div 
      class="bg-background rounded-lg shadow-lg w-full max-w-md mx-4 overflow-hidden"
      role="dialog"
      aria-modal="true"
    >
      <div class="p-6">
        <h2 class="text-xl font-semibold text-foreground mb-4">Settings</h2>

        <!-- Dark Mode Toggle Row -->
        <div class="flex items-center justify-between border border-background1 p-3 rounded-md">
          <span class="text-foreground font-medium">Dark Mode</span>
          <Switch bind:checked={isDark} />
        </div>

        <div class="flex justify-end mt-6">
          <Button
            onclick={onClose}
            variant="secondary"
            size="default"
            class="close-button"
            aria-label="Close Settings"
            title="Click to close settings"
          >
            Close
          </Button>
        </div>
      </div>
    </div>
  </div>
{/if}
