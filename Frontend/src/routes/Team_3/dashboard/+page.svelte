<script>
    import { onMount, tick } from 'svelte';
    import CreateProjectModal from '$lib/components/ui/dialog/CreateProjectModal.svelte';
    import ImportProjectModal from '$lib/components/ui/dialog/ImportProjectModal.svelte';

    let projects = [];
    let isLoading = true;
    let error = null;
    let analystInitials = '';
    let analystId = '';
    let showCreateModal = false;
    let showImportModal = false;

    onMount(async () => {
        analystInitials = localStorage.getItem('analyst_initials') || '';
        analystId = localStorage.getItem('analyst_id') || '';

        if (!analystInitials || !analystId) {
            window.location.href = '/login';
            return;
        }

        await loadProjects();
    });

    async function loadProjects() {
        isLoading = true;
        error = null;

        try {
            const response = await fetch(`http://127.0.0.1:8000/projects/analyst/${analystId}`);
            if (!response.ok) throw new Error('Failed to load projects');
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

            const response = await fetch('http://127.0.0.1:8000/projects/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
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
            if (!response.ok) throw new Error(responseData.detail || 'Failed to create project');

            await loadProjects();
            closeCreateModal();
        } catch (err) {
            console.error('Error creating project:', err);
            error = err.message;
        }
    }

    function handleImportProject(event) {
        const { files } = event.detail;
        console.log('Importing project files:', files);
        showImportModal = false;
    }

    function handleLogout() {
        localStorage.removeItem('analyst_id');
        localStorage.removeItem('analyst_initials');
        window.location.href = '/login';
    }
</script>

<div class="p-6">
    <header class="flex justify-between items-center mb-8">
        <h1 class="text-3xl font-bold">TRACE Dashboard</h1>
        <div class="flex items-center gap-4">
            <span class="text-sm text-muted-foreground">Analyst: {analystInitials}</span>
            <button
                    class="text-sm font-medium bg-red-500 text-white px-3 py-1 rounded-md hover:bg-red-600"
                    on:click={handleLogout}
            >
                Logout
            </button>
        </div>
    </header>

    <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-semibold">Your Projects</h2>
        <button
                class="bg-primary text-white text-sm font-medium px-4 py-2 rounded-md shadow hover:bg-primary/90"
                on:click={openCreateModal}
        >
            Create New Project
        </button>
    </div>

    {#if isLoading}
        <div class="text-gray-500">Loading projects...</div>
    {:else if error}
        <div class="text-red-500">Error: {error}</div>
    {:else if projects.length === 0}
        <div class="text-center mt-12 space-y-4">
            <p class="text-lg">You don't have any projects yet.</p>
            <button
                    class="bg-primary text-white px-4 py-2 rounded-md shadow hover:bg-primary/90"
                    on:click={openCreateModal}
            >
                Create Your First Project
            </button>
        </div>
    {:else}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {#each projects as project (project.id)}
                <div class="border border-border rounded-2xl p-4 shadow-sm bg-card space-y-2">
                    <h3 class="text-lg font-semibold">{project.name}</h3>
                    <p class="text-sm text-muted-foreground">{project.description || 'No description'}</p>
                    <div class="text-sm text-muted-foreground">
                        <span>Start: {project.start_date || 'N/A'}</span> ·
                        <span>End: {project.end_date || 'N/A'}</span>
                    </div>
                    <div class="text-sm">
                        Status:
                        <span class={project.locked ? 'text-red-500' : 'text-green-500'}>
              {project.locked ? 'Locked' : 'Unlocked'}
            </span>
                    </div>
                    <button class="w-full bg-secondary hover:bg-secondary/80 text-sm font-medium py-2 rounded-md">
                        View Project
                    </button>
                </div>
            {/each}
        </div>
    {/if}

    {#if showCreateModal}
        <CreateProjectModal
                analystId={analystId}
                on:close={closeCreateModal}
                on:create={handleProjectCreated}
        />
    {/if}

    {#if showImportModal}
        <ImportProjectModal
                on:close={() => (showImportModal = false)}
                on:import={handleImportProject}
        />
    {/if}
</div>
