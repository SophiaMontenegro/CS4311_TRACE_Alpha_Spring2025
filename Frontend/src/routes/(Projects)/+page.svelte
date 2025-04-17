<script>
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';

  let isDark = false;

  onMount(() => {
      isDark = document.documentElement.classList.contains('dark');
  });

  function toggleTheme() {
      isDark = !isDark;
      document.documentElement.classList.toggle('dark', isDark);
      localStorage.setItem('theme', isDark ? 'dark' : 'light');
  }

  function handleLogoClick() {
      const isSessionActive = false;
      if (isSessionActive) {
          if (confirm("You have an active session. Are you sure you want to leave?")) {
              goto('/dashboard');
          }
      } else {
          goto('/dashboard');
      }
  }
</script>

<div class="min-h-screen flex flex-col bg-background text-foreground px-6 py-4">
  <!-- Header -->
  <div class="flex justify-between items-center mb-8">
      <!-- Logo Image Toggle -->
      <div
              class="cursor-pointer w-32"
              on:click={handleLogoClick}
              title="Click to go to dashboard"
      >
          <!-- Light mode logo -->
          <img src="/icons/traceLightIcon.svg" alt="TRACE Logo" class="block dark:hidden" />

          <!-- Dark mode logo -->
          <img src="/icons/traceDarkIcon.svg" alt="TRACE Logo Dark" class="hidden dark:block" />
      </div>

      <!-- Nav + Theme Toggle -->
      <div class="flex items-center gap-4">
          <button class="hover:underline text-sm" title="Click to view dashboard" on:click={() => goto('/dashboard')}>
              Dashboard
          </button>
          <button class="hover:underline text-sm" title="Click to access settings" on:click={() => goto('/settings')}>
              Settings
          </button>
          <button
                  class="hover:underline text-sm"
                  on:click={toggleTheme}
                  title="Toggle dark/light mode"
          >
              {isDark ? '☀️' : '🌙'}
          </button>
      </div>
  </div>

  <!-- Main content -->
  <div class="flex flex-col items-center justify-center text-center flex-grow">
      <h1 class="text-4xl font-bold mb-4">Elevate Your Security Strategy with TRACE</h1>
      <p class="max-w-xl text-lg text-muted-foreground mb-6">
          A Cybersecurity Platform to Protect Your Digital Assets.
          Detect Vulnerabilities, Strengthen Defense, and Secure Your Network Seamlessly.
          Gain Real-Time Insights and Proactive Protection.
      </p>

      <button
              class="bg-[var(--accent)] text-[var(--accent-foreground)] px-6 py-3 rounded-xl hover:bg-[var(--accent3-hover)] transition"
              title="Click to start a session"
              on:click={() => goto('/login')}
      >
          START
      </button>
  </div>
</div>
