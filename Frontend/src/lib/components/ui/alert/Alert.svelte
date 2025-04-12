<script>
  // Props for the component
  export let isOpen = false;
  export let title = " ";
  export let message = " ";
  export let onCancel = () => {
    isOpen = false;
  };
  export let onContinue = () => {
    isOpen = false;
  };

  function handleBackdropClick(event) {
    if (event.target === event.currentTarget) {
      onCancel();
    }
  }

  function handleKeydown(event) {
    if (event.key === 'Escape') {
      onCancel();
    }
  }
</script>

<svelte:window on:keydown={handleKeydown} />

{#if isOpen}
  <div 
    class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
    role="button"
    tabindex="0"
    on:click={handleBackdropClick}
    on:keydown={(event) => event.key === 'Enter' && handleBackdropClick(event)}
  >
    <div 
      class="bg-background rounded-lg shadow-lg w-full max-w-md mx-4 overflow-hidden"
      role="alertdialog"
      aria-modal="true"
      aria-labelledby="alert-title"
      aria-describedby="alert-message"
    >
      <div class="p-6">
        <h2 id="alert-title" class="text-xl font-semibold text-foreground mb-2">{title}</h2>
        <p id="alert-message" class="text-foreground mb-6">{message}</p>
        
        <div class="flex justify-end gap-3">
          <button 
            class="px-4 py-2 rounded-md bg-accent text-background hover:bg-accent1 transition-colors"
            on:click={onCancel}
          >
            Cancel
          </button>
          <button 
            class="px-4 py-2 rounded-md bg-background1 text-foreground hover:bg-background2 transition-colors"
            on:click={onContinue}
          >
            Continue
          </button>
        </div>
      </div>
    </div>
  </div>
{/if}