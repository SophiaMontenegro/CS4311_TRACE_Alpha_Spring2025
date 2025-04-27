<!-- <script>
  import { onMount } from 'svelte';
  import ThemeToggle from '$lib/components/ThemeToggle.svelte';
  
  // Deleted projects data (mock data for now)
  let deletedProjects = [
    { id: 1, name: 'Network Security Audit', deletedDate: '2024-02-15', leadAnalyst: 'JD' },
    { id: 2, name: 'Vulnerability Assessment', deletedDate: '2024-02-10', leadAnalyst: 'MK' },
    { id: 3, name: 'Penetration Testing', deletedDate: '2024-02-05', leadAnalyst: 'LE' },
    { id: 4, name: 'Security Policy Review', deletedDate: '2024-01-28', leadAnalyst: 'JD' },
    { id: 5, name: 'Incident Response Plan', deletedDate: '2024-01-20', leadAnalyst: 'MK' },
    { id: 6, name: 'Compliance Audit', deletedDate: '2024-01-15', leadAnalyst: 'LE' }
  ];
  
  // Search and filter
  let searchQuery = '';
  let sortField = 'deletedDate'; // 'name', 'deletedDate', or 'leadAnalyst'
  let sortDirection = 'desc'; // 'asc' or 'desc'
  
  // Filtered and sorted projects
  $: filteredProjects = deletedProjects
    .filter(project => project.name.toLowerCase().includes(searchQuery.toLowerCase()))
    .sort((a, b) => {
      let comparison = 0;
      
      if (sortField === 'name') {
        comparison = a.name.localeCompare(b.name);
      } else if (sortField === 'deletedDate') {
        comparison = new Date(a.deletedDate) - new Date(b.deletedDate);
      } else if (sortField === 'leadAnalyst') {
        comparison = a.leadAnalyst.localeCompare(b.leadAnalyst);
      }
      
      return sortDirection === 'asc' ? comparison : -comparison;
    });
  
  // Function to handle sorting
  function handleSort(field) {
    if (sortField === field) {
      // Toggle direction if clicking the same field
      sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      // Set new field and default to descending
      sortField = field;
      sortDirection = 'desc';
    }
  }
  
  // Function to handle project options
  function handleProjectOption(projectId, action) {
    if (action === 'restore') {
      console.log(`Restoring project ${projectId}`);
      // Implement actual restore functionality later
    } else if (action === 'deleteForever') {
      if (confirm(`Are you sure you want to permanently delete this project? This action cannot be undone.`)) {
        console.log(`Permanently deleting project ${projectId}`);
        // Implement actual permanent deletion later
      }
    }
  }
</script>

<div class="deleted-container">
  <header class="deleted-header">
    <h1>Deleted Projects</h1>
    <div class="header-actions">
      <div class="search-filter">
        <input 
          type="text" 
          placeholder="Search deleted projects..." 
          bind:value={searchQuery}
        />
      </div>
      <ThemeToggle />
    </div>
  </header>
  
  <div class="deleted-projects">
    {#if filteredProjects.length === 0}
      <p class="no-projects">No deleted projects found matching your criteria.</p>
    {:else}
      <div class="projects-table">
        <div class="table-header">
          <div class="header-cell name" on:click={() => handleSort('name')}>
            Project Name
            {#if sortField === 'name'}
              <span class="sort-indicator">{sortDirection === 'asc' ? '↑' : '↓'}</span>
            {/if}
          </div>
          <div class="header-cell date" on:click={() => handleSort('deletedDate')}>
            Deleted Date
            {#if sortField === 'deletedDate'}
              <span class="sort-indicator">{sortDirection === 'asc' ? '↑' : '↓'}</span>
            {/if}
          </div>
          <div class="header-cell analyst" on:click={() => handleSort('leadAnalyst')}>
            Lead Analyst
            {#if sortField === 'leadAnalyst'}
              <span class="sort-indicator">{sortDirection === 'asc' ? '↑' : '↓'}</span>
            {/if}
          </div>
          <div class="header-cell actions">
            Actions
          </div>
        </div>
        
        {#each filteredProjects as project}
          <div class="project-row">
            <div class="cell name">{project.name}</div>
            <div class="cell date">{project.deletedDate}</div>
            <div class="cell analyst">
              <div class="analyst-badge">{project.leadAnalyst}</div>
            </div>
            <div class="cell actions">
              <div class="options-menu">
                <button class="options-btn" title="More options">⋯</button>
                <div class="dropdown-content">
                  <button 
                    on:click={() => handleProjectOption(project.id, 'restore')}
                    title="Restore this project to your active projects"
                  >
                    Restore
                  </button>
                  <button 
                    class="delete-forever"
                    on:click={() => handleProjectOption(project.id, 'deleteForever')}
                    title="Permanently delete this project (cannot be undone)"
                  >
                    Delete Forever
                  </button>
                </div>
              </div>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </div>
</div>

<style>
  .deleted-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
  }
  
  .deleted-header {
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
  
  input {
    padding: 8px 12px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 14px;
    min-width: 250px;
  }
  
  :global(body.dark-mode) input {
    background-color: #2a2a2a;
    border-color: #444;
    color: #e0e0e0;
  }
  
  .deleted-projects {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    overflow: hidden;
  }
  
  :global(body.dark-mode) .deleted-projects {
    background-color: #1e1e1e;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  }
  
  .projects-table {
    width: 100%;
    border-collapse: collapse;
  }
  
  .table-header {
    display: flex;
    background-color: #f5f5f5;
    border-bottom: 1px solid #ddd;
    font-weight: bold;
  }
  
  :global(body.dark-mode) .table-header {
    background-color: #2a2a2a;
    border-bottom-color: #444;
  }
  
  .header-cell {
    padding: 15px;
    cursor: pointer;
    display: flex;
    align-items: center;
    color: #555;
    transition: background-color 0.2s ease;
  }
  
  :global(body.dark-mode) .header-cell {
    color: #b0b0b0;
  }
  
  .header-cell:hover {
    background-color: #e9e9e9;
  }
  
  :global(body.dark-mode) .header-cell:hover {
    background-color: #333;
  }
  
  .sort-indicator {
    margin-left: 5px;
  }
  
  .project-row {
    display: flex;
    border-bottom: 1px solid #eee;
    transition: background-color 0.2s ease;
  }
  
  :global(body.dark-mode) .project-row {
    border-bottom-color: #333;
  }
  
  .project-row:hover {
    background-color: #f9f9f9;
  }
  
  :global(body.dark-mode) .project-row:hover {
    background-color: #252525;
  }
  
  .cell {
    padding: 15px;
    display: flex;
    align-items: center;
  }
  
  .name {
    flex: 3;
    color: #333;
  }
  
  :global(body.dark-mode) .name {
    color: #fff;
  }
  
  .date {
    flex: 1;
    color: #777;
  }
  
  :global(body.dark-mode) .date {
    color: #aaa;
  }
  
  .analyst {
    flex: 1;
    justify-content: center;
  }
  
  .actions {
    flex: 1;
    justify-content: center;
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
  }
  
  :global(body.dark-mode) .analyst-badge {
    background-color: #444;
    color: #e0e0e0;
  }
  
  .options-menu {
    position: relative;
    display: inline-block;
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
    background-color: white;
    min-width: 150px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
    z-index: 1;
    border-radius: 4px;
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
    padding: 10px 15px;
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
  
  .delete-forever {
    color: #f44336 !important;
  }
  
  :global(body.dark-mode) .delete-forever {
    color: #ff6b6b !important;
  }
  
  .no-projects {
    text-align: center;
    padding: 30px;
    color: #777;
  }
  
  :global(body.dark-mode) .no-projects {
    color: #aaa;
  }
</style> -->