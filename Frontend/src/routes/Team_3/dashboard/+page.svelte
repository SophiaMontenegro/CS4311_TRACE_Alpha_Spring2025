<script>
  import { onMount } from 'svelte';
  import { tick } from 'svelte';
  import ThemeToggle from '$lib/components/ThemeToggle.svelte';
  import CreateProjectModal from '$lib/components/CreateProjectModal.svelte';
  import ImportProjectModal from '$lib/components/ImportProjectModal.svelte';
  
  // Project data (mock data for now)
  let recentProjects = [
    { id: 1, name: 'Network Security Audit', lastEdit: '2024-02-15', status: 'active', leadAnalyst: 'JD' },
    { id: 2, name: 'Vulnerability Assessment', lastEdit: '2024-02-10', status: 'error', leadAnalyst: 'MK' },
    { id: 3, name: 'Penetration Testing', lastEdit: '2024-02-05', status: 'inactive', leadAnalyst: 'LE' }
  ];
  
  let allProjects = [
    { id: 1, name: 'Network Security Audit', lastEdit: '2024-02-15', status: 'active', leadAnalyst: 'JD' },
    { id: 2, name: 'Vulnerability Assessment', lastEdit: '2024-02-10', status: 'error', leadAnalyst: 'MK' },
    { id: 3, name: 'Penetration Testing', lastEdit: '2024-02-05', status: 'inactive', leadAnalyst: 'LE' },
    { id: 4, name: 'Security Policy Review', lastEdit: '2024-01-28', status: 'active', leadAnalyst: 'JD' },
    { id: 5, name: 'Incident Response Plan', lastEdit: '2024-01-20', status: 'active', leadAnalyst: 'MK' },
    { id: 6, name: 'Compliance Audit', lastEdit: '2024-01-15', status: 'inactive', leadAnalyst: 'LE' }
  ];
  
  // Updated shared projects with port numbers and access status
  let sharedProjects = [
    { id: 7, name: 'Shared Security Assessment', lastEdit: '2024-02-12', status: 'active', leadAnalyst: 'RJ', port: 8080, canAccess: true },
    { id: 8, name: 'Team Vulnerability Scan', lastEdit: '2024-02-08', status: 'active', leadAnalyst: 'TM', port: 8081, canAccess: true },
    { id: 9, name: 'Enterprise Risk Analysis', lastEdit: '2024-02-05', status: 'active', leadAnalyst: 'KL', port: 8082, canAccess: false },
    { id: 10, name: 'Collaborative Threat Hunting', lastEdit: '2024-01-30', status: 'active', leadAnalyst: 'BM', port: 8083, canAccess: true }
  ];
  
  // Active tab state
  let activeTab = 'myProjects';
  
  // Search and filter
  let searchQuery = '';
  let statusFilter = 'all';
  
  // Filtered projects based on search and filter
  $: filteredProjects = (activeTab === 'myProjects' ? allProjects : sharedProjects)
    .filter(project => {
      // Filter by search query
      const matchesSearch = project.name.toLowerCase().includes(searchQuery.toLowerCase());
      
      // Filter by status
      const matchesStatus = statusFilter === 'all' || project.status === statusFilter;
      
      return matchesSearch && matchesStatus;
    });
  
  // Function to handle run scan
  function runScan(projectId) {
    console.log(`Running scan for project ${projectId}`);
    // Implement actual scan functionality later
  }
  
  // Function to join shared project
  function joinProject(projectId, port) {
    console.log(`Joining project ${projectId} on port ${port}`);
    // Implement actual join functionality later
  }

  // Show/hide create project modal
  let showCreateModal = false;
  // Add the missing showImportModal variable
  let showImportModal = false;
  
  // Function to handle create project
  function handleCreateProject(event) {
    const projectData = event.detail;
    console.log('Creating new project:', projectData);
    
    // Here you would typically send this data to your backend
    // For now, we'll just add it to our projects array
    const newProject = {
      id: allProjects.length + 1,
      name: projectData.projectName,
      lastEdit: new Date().toISOString().split('T')[0],
      status: 'active',
      leadAnalyst: projectData.leadAnalyst
    };
    
    allProjects = [newProject, ...allProjects];
    recentProjects = [newProject, ...recentProjects.slice(0, 2)];
    
    // Close the modal
    tick().then(() => {
        showCreateModal = false; // Ensure state updates
    });
  }
  
  // Function to handle import project
  function handleImportProject(event) {
    const { files } = event.detail;
    console.log('Importing project files:', files);
    
    // Here you would typically process the files and create projects from them
    // For now, we'll just add a mock project
    const newProject = {
      id: allProjects.length + 1,
      name: `Imported Project ${allProjects.length + 1}`,
      lastEdit: new Date().toISOString().split('T')[0],
      status: 'active',
      leadAnalyst: 'IM'
    };
    
    allProjects = [newProject, ...allProjects];
    recentProjects = [newProject, ...recentProjects.slice(0, 2)];
    
    // Close the modal
    showImportModal = false;
  }
  
  // Function to create new project
  function createNewProject() {
    showCreateModal = true;
  }
  
  // Function to import project
  function importProject() {
    showImportModal = true;
  }

  let projects = []; // List of projects
  let isLoading = true;
  let error = null;
  let analystInitials = '';
  let analystId = '';

  // Load projects on mount
  onMount(async () => {
    // Get analyst info from localStorage
    analystInitials = localStorage.getItem('analyst_initials') || '';
    analystId = localStorage.getItem('analyst_id') || '';
    
    if (!analystInitials || !analystId) {
      // Redirect to login if no analyst info is found
      window.location.href = '/login';
      return;
    }
    
    await loadProjects();
  });

  async function loadProjects() {
    isLoading = true;
    error = null;
    
    try {
      // Fetch projects for the logged-in analyst
      const response = await fetch(`http://127.0.0.1:8000/projects/analyst/${analystId}`);
      
      if (!response.ok) {
        throw new Error('Failed to load projects');
      }
      
      const data = await response.json();
      projects = data.projects || [];
    } catch (err) {
      console.error('Error loading projects:', err);
      error = err.message;
      projects = [];
    } finally {
      isLoading = false;
    }
  }
  
  function openCreateModal() {
    showCreateModal = true;
  }
  
  function closeCreateModal() {
    showCreateModal = false;
  }
  
  async function handleProjectCreated(event) {
    try {
      const projectData = event.detail;
      console.log('Creating new project:', projectData);
      
      // Create project on the backend - ensure data format matches API expectations
      const response = await fetch('http://127.0.0.1:8000/projects/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          analyst_id: analystId,
          project_name: projectData.name,
          start_date: projectData.startDate,
          end_date: projectData.endDate,
          description: projectData.description || '',
          userList: projectData.userList || []
        })
      });
      
      const responseData = await response.json();
      console.log('Project creation response:', responseData);
      
      if (!response.ok) {
        throw new Error(responseData.detail || 'Failed to create project');
      }
      
      // Reload projects to get the newly created one
      await loadProjects();
      closeCreateModal();
    } catch (err) {
      console.error('Error creating project:', err);
      error = err.message;
    }
  }
  
  function handleLogout() {
    // Clear localStorage and redirect to login
    localStorage.removeItem('analyst_id');
    localStorage.removeItem('analyst_initials');
    window.location.href = '/login';
  }
</script>

<div class="dashboard">
  <header>
    <div class="header-content">
      <h1>TRACE Dashboard</h1>
      <div class="user-controls">
        <span class="analyst-info">Analyst: {analystInitials}</span>
        <button class="logout-btn" on:click={handleLogout}>Logout</button>
        <ThemeToggle />
      </div>
    </div>
  </header>
  
  <main>
    <div class="dashboard-header">
      <h2>Your Projects</h2>
      <button class="create-btn" on:click={openCreateModal}>Create New Project</button>
    </div>
    
    {#if isLoading}
      <div class="loading">Loading projects...</div>
    {:else if error}
      <div class="error">Error: {error}</div>
    {:else if projects.length === 0}
      <div class="no-projects">
        <p>You don't have any projects yet.</p>
        <button class="create-btn" on:click={openCreateModal}>Create Your First Project</button>
      </div>
    {:else}
      <div class="project-grid">
        {#each projects as project (project.id)}
          <div class="project-card">
            <h3>{project.name}</h3>
            <p>{project.description || 'No description'}</p>
            <div class="project-dates">
              <span>Start: {project.start_date || 'N/A'}</span>
              <span>End: {project.end_date || 'N/A'}</span>
            </div>
            <div class="project-status">
              Status: {project.locked ? 'Locked' : 'Unlocked'}
            </div>
            <button class="view-btn">View Project</button>
          </div>
        {/each}
      </div>
    {/if}
  </main>
  
  {#if showCreateModal}
    <CreateProjectModal 
      analystId={analystId}
      on:close={closeCreateModal}
      on:create={handleProjectCreated}
    />
  {/if}
  
  {#if showImportModal}
    <ImportProjectModal 
      on:close={() => showImportModal = false}
      on:import={handleImportProject}
    />
  {/if}
</div>

<style>
  /* Dashboard styles */
  .dashboard {
    min-height: 100vh;
    background-color: #f5f5f5;
    transition: background-color 0.3s ease;
  }
  
  :global(body.dark-mode) .dashboard {
    background-color: #121212;
  }
  
  header {
    background-color: white;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    padding: 1rem 2rem;
    transition: background-color 0.3s ease, box-shadow 0.3s ease;
  }
  
  :global(body.dark-mode) header {
    background-color: #1e1e1e;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  }
  
  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    max-width: 1200px;
    margin: 0 auto;
  }
  
  h1 {
    margin: 0;
    color: #333;
  }
  
  :global(body.dark-mode) h1 {
    color: #ffffff;
  }
  
  .user-controls {
    display: flex;
    align-items: center;
    gap: 1rem;
  }
  
  .analyst-info {
    color: #555;
    font-weight: 500;
  }
  
  :global(body.dark-mode) .analyst-info {
    color: #b0b0b0;
  }
  
  .logout-btn {
    background: none;
    border: 1px solid #ccc;
    border-radius: 4px;
    padding: 0.5rem 1rem;
    cursor: pointer;
    color: #555;
    transition: all 0.2s ease;
  }
  
  :global(body.dark-mode) .logout-btn {
    border-color: #444;
    color: #b0b0b0;
  }
  
  .logout-btn:hover {
    background-color: #f0f0f0;
  }
  
  :global(body.dark-mode) .logout-btn:hover {
    background-color: #2a2a2a;
  }
  
  main {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
  }
  
  .dashboard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
  }
  
  h2 {
    margin: 0;
    color: #333;
  }
  
  :global(body.dark-mode) h2 {
    color: #ffffff;
  }
  
  .create-btn {
    background-color: #4a56e2;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 0.75rem 1.5rem;
    cursor: pointer;
    font-size: 1rem;
    transition: background-color 0.3s ease;
  }
  
  .create-btn:hover {
    background-color: #3a46c2;
  }
  
  :global(body.dark-mode) .create-btn:hover {
    background-color: #5a66f2;
  }
  
  .project-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 2rem;
  }
  
  .project-card {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    padding: 1.5rem;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
  }
  
  :global(body.dark-mode) .project-card {
    background-color: #1e1e1e;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  }
  
  .project-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  }
  
  :global(body.dark-mode) .project-card:hover {
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.4);
  }
  
  .project-card h3 {
    margin-top: 0;
    margin-bottom: 0.5rem;
    color: #333;
  }
  
  :global(body.dark-mode) .project-card h3 {
    color: #ffffff;
  }
  
  .project-card p {
    color: #666;
    margin-bottom: 1rem;
  }
  
  :global(body.dark-mode) .project-card p {
    color: #aaa;
  }
  
  .project-dates {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
    color: #777;
  }
  
  :global(body.dark-mode) .project-dates {
    color: #999;
  }
  
  .project-status {
    margin-bottom: 1rem;
    font-weight: 500;
    color: #555;
  }
  
  :global(body.dark-mode) .project-status {
    color: #bbb;
  }
  
  .view-btn {
    width: 100%;
    padding: 0.5rem;
    background-color: #4a56e2;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.3s ease;
  }
  
  .view-btn:hover {
    background-color: #3a46c2;
  }
  
  :global(body.dark-mode) .view-btn:hover {
    background-color: #5a66f2;
  }
  
  .loading, .error, .no-projects {
    text-align: center;
    padding: 3rem;
    color: #555;
  }
  
  :global(body.dark-mode) .loading, 
  :global(body.dark-mode) .error, 
  :global(body.dark-mode) .no-projects {
    color: #b0b0b0;
  }
  
  .error {
    color: #f44336;
  }
  
  .no-projects {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.5rem;
  }
  
  .no-projects button {
    width: auto;
  }
</style>