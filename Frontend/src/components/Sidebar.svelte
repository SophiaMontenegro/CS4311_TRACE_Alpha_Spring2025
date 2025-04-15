<script>
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import ThemeToggle from './ThemeToggle.svelte';
  
  // Track active section based on URL
  $: activeSection = $page.url.pathname.includes('/folders') 
    ? 'folders' 
    : $page.url.pathname.includes('/deleted') 
      ? 'deleted' 
      : $page.url.pathname.includes('/settings') 
        ? 'settings' 
        : 'projects';
  
  // Navigation items
  const navItems = [
    { id: 'projects', name: 'Project Selection', icon: '📁', hoverText: 'Access available projects' },
    { id: 'folders', name: 'Project Folders', icon: '📂', hoverText: 'Browse project folders' },
    { id: 'deleted', name: 'Deleted Projects', icon: '🗑️', hoverText: 'View deleted projects' },
    { id: 'settings', name: 'Settings', icon: '⚙️', hoverText: 'Adjust application settings' }
  ];
  
  function navigateTo(sectionId) {
    if (sectionId === 'projects') {
      goto('/dashboard');
    } else if (sectionId === 'folders') {
      goto('/dashboard/folders');
    } else if (sectionId === 'deleted') {
      goto('/dashboard/deleted');
    } else if (sectionId === 'settings') {
      goto('/dashboard/settings');
    }
  }
  
  function goToHome() {
    goto('/');
  }
</script>

<aside class="sidebar">
  <!-- TRACE logo at the top -->
  <div class="logo-container" on:click={goToHome} title="Return to home page">
    <span class="logo">TRACE</span>
  </div>
  
  <!-- Navigation items -->
  <nav class="nav-items">
    {#each navItems as item}
      <button 
        class="nav-item {activeSection === item.id ? 'active' : ''}"
        on:click={() => navigateTo(item.id)}
        title={item.hoverText}
      >
        <span class="icon">{item.icon}</span>
        <span class="name">{item.name}</span>
      </button>
    {/each}
  </nav>
  
  <div class="sidebar-footer">
    <ThemeToggle />
  </div>
</aside>

<style>
  .sidebar {
    width: 250px;
    height: 100vh;
    background-color: #f5f5f5;
    border-right: 1px solid #e0e0e0;
    display: flex;
    flex-direction: column;
    transition: background-color 0.3s ease;
  }
  
  :global(body.dark-mode) .sidebar {
    background-color: #1e1e1e;
    border-right-color: #333;
  }
  
  .logo-container {
    padding: 20px;
    text-align: center;
    border-bottom: 1px solid #e0e0e0;
    cursor: pointer;
  }
  
  :global(body.dark-mode) .logo-container {
    border-bottom-color: #333;
  }
  
  .logo {
    font-size: 24px;
    font-weight: bold;
    color: #4a56e2;
  }
  
  :global(body.dark-mode) .logo {
    color: #7b85ff;
  }
  
  .nav-items {
    display: flex;
    flex-direction: column;
    padding: 20px 0;
    /* Consistent spacing between items */
    gap: 15px;
  }
  
  .nav-item {
    display: flex;
    align-items: center;
    padding: 12px 20px;
    border: none;
    background: none;
    cursor: pointer;
    transition: background-color 0.2s ease;
    border-left: 3px solid transparent;
    text-align: left;
    width: 100%;
  }
  
  .nav-item:hover {
    background-color: #e9e9e9;
  }
  
  :global(body.dark-mode) .nav-item:hover {
    background-color: #2a2a2a;
  }
  
  .nav-item.active {
    background-color: #e3e6ff;
    border-left-color: #4a56e2;
    font-weight: 500;
  }
  
  :global(body.dark-mode) .nav-item.active {
    background-color: #2a2d4a;
    border-left-color: #7b85ff;
  }
  
  .icon {
    font-size: 20px;
    margin-right: 12px;
    width: 24px;
    text-align: center;
  }
  
  .name {
    font-size: 14px;
    color: #333;
  }
  
  :global(body.dark-mode) .name {
    color: #e0e0e0;
  }
  
  .sidebar-footer {
    margin-top: auto;
    padding: 20px;
    display: flex;
    justify-content: center;
    border-top: 1px solid #e0e0e0;
  }
  
  :global(body.dark-mode) .sidebar-footer {
    border-top-color: #333;
  }
</style>