<script>
  import { onMount } from 'svelte';
  import ThemeToggle from '$lib/components/ThemeToggle.svelte';
  
  // Folder data (mock data for now)
  let recentFolders = [
    { id: 1, name: 'Network Security', created: '2024-02-15', leadAnalyst: 'JD' },
    { id: 2, name: 'Vulnerability Assessments', created: '2024-02-10', leadAnalyst: 'MK' },
    { id: 3, name: 'Penetration Testing', created: '2024-02-05', leadAnalyst: 'LE' }
  ];
  
  let allFolders = [
    { id: 1, name: 'Network Security', created: '2024-02-15', leadAnalyst: 'JD' },
    { id: 2, name: 'Vulnerability Assessments', created: '2024-02-10', leadAnalyst: 'MK' },
    { id: 3, name: 'Penetration Testing', created: '2024-02-05', leadAnalyst: 'LE' },
    { id: 4, name: 'Security Policies', created: '2024-01-28', leadAnalyst: 'JD' },
    { id: 5, name: 'Incident Response', created: '2024-01-20', leadAnalyst: 'MK' },
    { id: 6, name: 'Compliance Audits', created: '2024-01-15', leadAnalyst: 'LE' },
    { id: 7, name: 'Risk Assessments', created: '2024-01-10', leadAnalyst: 'RJ' },
    { id: 8, name: 'Threat Intelligence', created: '2024-01-05', leadAnalyst: 'TM' }
  ];
  
  // Search and filter
  let searchQuery = '';
  let sortOrder = 'alphabetical'; // 'alphabetical' or 'date'
  
  // Filtered and sorted folders
  $: filteredFolders = allFolders
    .filter(folder => folder.name.toLowerCase().includes(searchQuery.toLowerCase()))
    .sort((a, b) => {
      if (sortOrder === 'alphabetical') {
        return a.name.localeCompare(b.name);
      } else {
        return new Date(b.created) - new Date(a.created);
      }
    });
  
  // Function to handle folder options
  function handleFolderOption(folderId, action) {
    console.log(`Performing ${action} on folder ${folderId}`);
    // Implement actual actions later
  }
  
  // Function to create new folder
  function createNewFolder() {
    console.log('Creating new folder');
    // Implement folder creation later
  }
  
  // Function to import folder
  function importFolder() {
    console.log('Importing folder');
    // Implement folder import later
  }
  
  // Function to open folder
  function openFolder(folderId) {
    console.log(`Opening folder ${folderId}`);
    // Implement folder opening later
  }
</script>

<div class="folders-container">
  <header class="folders-header">
    <h1>Project Folders</h1>
    <div class="header-actions">
      <div class="search-filter">
        <input 
          type="text" 
          placeholder="Search folders..." 
          bind:value={searchQuery}
        />
        <select bind:value={sortOrder}>
          <option value="alphabetical">Sort: A-Z</option>
          <option value="date">Sort: Recent First</option>
        </select>
      </div>
      <button class="import-btn" on:click={importFolder} title="Import folder">
        <span class="icon">📥</span>
      </button>
      <button class="create-btn" on:click={createNewFolder}>Create New</button>
      <ThemeToggle />
    </div>
  </header>
  
  <section class="recent-folders">
    <h2>Recent Folders</h2>
    <div class="folder-cards">
      {#each recentFolders as folder}
        <div class="folder-card" on:click={() => openFolder(folder.id)}>
          <div class="folder-icon">📁</div>
          <div class="folder-info">
            <h3>{folder.name}</h3>
            <p>Created: {folder.created}</p>
          </div>
        </div>
      {/each}
    </div>
  </section>
  
  <section class="all-folders">
    <h2>All Folders</h2>
    
    {#if filteredFolders.length === 0}
      <p class="no-folders">No folders found matching your criteria.</p>
    {:else}
      <div class="folder-grid">
        {#each filteredFolders as folder}
          <div class="folder-item" on:click={() => openFolder(folder.id)}>
            <div class="folder-icon">📁</div>
            <div class="folder-details">
              <h3>{folder.name}</h3>
              <p>Created: {folder.created}</p>
              <div class="analyst-badge">{folder.leadAnalyst}</div>
            </div>
            <div class="options-menu" on:click|stopPropagation>
              <button class="options-btn" title="More options">⋯</button>
              <div class="dropdown-content">
                <button 
                  on:click={() => handleFolderOption(folder.id, 'rename')}
                  title="Rename this folder"
                >
                  Rename
                </button>
                <button 
                  on:click={() => handleFolderOption(folder.id, 'move')}
                  title="Move this folder to another location"
                >
                  Move
                </button>
                <button 
                  on:click={() => handleFolderOption(folder.id, 'delete')}
                  title="Delete this folder"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </section>
</div>

<style>
  .folders-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
  }
  
  .folders-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
  }
  
  h1 {
    font-size: 24px;
    margin: 0;
    color: #333;
  }
  
  :global(body.dark-mode) h1 {
    color: #fff;
  }
  
  .header-actions {
    display: flex;
    align-items: center;
    gap: 15px;
  }
  
  .search-filter {
    display: flex;
    gap: 10px;
  }
  
  input, select {
    padding: 8px 12px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 14px;
  }
  
  :global(body.dark-mode) input,
  :global(body.dark-mode) select {
    background-color: #2a2a2a;
    border-color: #444;
    color: #e0e0e0;
  }
  
  .create-btn, .import-btn {
    padding: 8px 15px;
    background-color: #4a56e2;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    display: flex;
    align-items: center;
    gap: 5px;
  }
  
  .import-btn {
    padding: 8px 10px;
  }
  
  .create-btn:hover, .import-btn:hover {
    background-color: #3a46c2;
  }
  
  :global(body.dark-mode) .create-btn:hover,
  :global(body.dark-mode) .import-btn:hover {
    background-color: #5a66f2;
  }
  
  h2 {
    font-size: 18px;
    margin-bottom: 15px;
    color: #555;
  }
  
  :global(body.dark-mode) h2 {
    color: #b0b0b0;
  }
  
  .recent-folders {
    margin-bottom: 30px;
  }
  
  .folder-cards {
    display: flex;
    gap: 20px;
    overflow-x: auto;
    padding-bottom: 10px;
  }
  
  .folder-card {
    min-width: 200px;
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    padding: 15px;
    display: flex;
    flex-direction: column;
    align-items: center;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    cursor: pointer;
  }
  
  :global(body.dark-mode) .folder-card {
    background-color: #1e1e1e;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  }
  
  .folder-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  }
  
  .folder-icon {
    font-size: 32px;
    margin-bottom: 10px;
    color: #4a56e2;
  }
  
  :global(body.dark-mode) .folder-icon {
    color: #7b85ff;
  }
  
  .folder-info {
    width: 100%;
    text-align: center;
  }
  
  .folder-info h3 {
    font-size: 16px;
    margin: 0 0 5px 0;
    color: #333;
  }
  
  :global(body.dark-mode) .folder-info h3 {
    color: #fff;
  }
  
  .folder-info p {
    font-size: 12px;
    color: #777;
    margin: 0;
  }
  
  :global(body.dark-mode) .folder-info p {
    color: #aaa;
  }
  
  .folder-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 20px;
  }
  
  .folder-item {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    padding: 15px;
    display: flex;
    flex-direction: column;
    position: relative;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    cursor: pointer;
  }
  
  :global(body.dark-mode) .folder-item {
    background-color: #1e1e1e;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  }
  
  .folder-item:hover {
    transform: translateY(-3px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  }
  
  .folder-details {
    margin-top: 10px;
  }
  
  .folder-details h3 {
    font-size: 16px;
    margin: 0 0 5px 0;
    color: #333;
  }
  
  :global(body.dark-mode) .folder-details h3 {
    color: #fff;
  }
  
  .folder-details p {
    font-size: 12px;
    color: #777;
    margin: 0 0 10px 0;
  }
  
  :global(body.dark-mode) .folder-details p {
    color: #aaa;
  }
  
  .analyst-badge {
    background-color: #e0e0e0;
    color: #333;
    width: 30px;
    height: 30px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 12px;
    position: absolute;
    top: 15px;
    right: 15px;
  }
  
  :global(body.dark-mode) .analyst-badge {
    background-color: #444;
    color: #e0e0e0;
  }
  
  .options-menu {
    position: absolute;
    bottom: 15px;
    right: 15px;
  }
  
  .options-btn {
    background: none;
    border: none;
    font-size: 20px;
    cursor: pointer;
    color: #555;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
  }
  
  :global(body.dark-mode) .options-btn {
    color: #b0b0b0;
  }
  
  .options-btn:hover {
    background-color: #f0f0f0;
  }
  
  :global(body.dark-mode) .options-btn:hover {
    background-color: #2a2a2a;
  }
  
  .dropdown-content {
    display: none;
    position: absolute;
    right: 0;
    bottom: 100%;
    background-color: white;
    min-width: 120px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
    z-index: 1;
    border-radius: 4px;
    margin-bottom: 5px;
  }
  
  :global(body.dark-mode) .dropdown-content {
    background-color: #2a2a2a;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.4);
  }
  
  .options-menu:hover .dropdown-content {
    display: block;
  }
  
  .dropdown-content button {
    width: 100%;
    text-align: left;
    padding: 8px 12px;
    background: none;
    border: none;
    cursor: pointer;
    font-size: 14px;
    color: #333;
  }
  
  :global(body.dark-mode) .dropdown-content button {
    color: #e0e0e0;
  }
  
  .dropdown-content button:hover {
    background-color: #f5f5f5;
  }
  
  :global(body.dark-mode) .dropdown-content button:hover {
    background-color: #3a3a3a;
  }
  
  .no-folders {
    text-align: center;
    padding: 20px;
    color: #777;
  }
  
  :global(body.dark-mode) .no-folders {
    color: #aaa;
  }
</style>