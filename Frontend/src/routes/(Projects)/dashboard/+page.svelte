<script>
    import { onMount, tick } from 'svelte';
    import CreateProjectModal from '$lib/components/ui/project_management/CreateProjectModal.svelte';
    import ImportProjectModal from '$lib/components/ui/project_management/ImportProjectModal.svelte';
    import EditProjectDialog from '$lib/components/ui/project_management/EditProjectDialog.svelte';
    import {Lock, Settings2, MoreHorizontal, Trash2, Import } from 'lucide-svelte';
    import { goto } from '$app/navigation';
    import { Button } from '$lib/components/ui/button';
    import Alert from '$lib/components/ui/alert/Alert.svelte';

    let projects = [];
    let isLoading = true;
    let error = null;
    let analystInitials = '';
    let analystId = '';
    let showCreateModal = false;
    let showImportModal = false;

    let editDialogOpen = false;
    let currentProject = null;

    let projectToDelete = null;
    let showDeleteDialog = false; //come back

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
            const response = await fetch(`http://127.0.0.1:8000/team3/projects/analyst/${analystId}`);
            if (!response.ok) throw new Error('Failed to load projects');
            const data = await response.json();
            projects = data.projects || [];
            console.log("Response data:", response.data);

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

            console.log(projectData);

            const response = await fetch('http://127.0.0.1:8000/team3/projects/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    analyst_id: analystInitials,
                    project_name: projectData.projectName,
                    start_date: projectData.startDate,
                    end_date: projectData.endDate,
                    description: projectData.description || '',
                    userList: projectData.userList || []
                })
            });

            const responseData = await response.json();
            if (!response.ok) {
                let errorMessage = 'Failed to create project';
                if (responseData.detail) {
                    // If it's a string or something printable
                    errorMessage = typeof responseData.detail === 'string'
                        ? responseData.detail
                        : JSON.stringify(responseData.detail);
                } else if (typeof responseData === 'object') {
                    errorMessage = JSON.stringify(responseData);
                }

                throw new Error(errorMessage);
            }


            await loadProjects();
            closeCreateModal();
        } catch (err) {
            if (err instanceof Error) {
                console.error("Error creating project:", err.message);
                error = err.message;
            } else {
                console.error("Unknown error creating project:", JSON.stringify(err, null, 2));
                error = 'An unknown error occurred';
            }
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

    async function toggleProjectLock(projectName) {
        console.log("Toggling lock for:", projectName, "by", analystInitials);
        try {
            const response = await fetch(`http://127.0.0.1:8000/team3/projects/${encodeURIComponent(projectName)}/lock?analyst_id=${analystInitials}`, {
                method: 'PUT'
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Failed to update lock status');
            }

            await loadProjects(); // Refresh projects list
        } catch (err) {
            console.error('Error toggling lock:', err);
            error = err.message;
        }
    }

    window.toggleProjectLock = toggleProjectLock;

    async function deleteProject(name) {
        console.log("Deleting project:", name); // Not working
        try {
            showDeleteDialog = false;
            const response = await fetch(`http://127.0.0.1:8000/team3/projects/${encodeURIComponent(name)}/delete?analyst_id=${analystId}`, {
                method: 'DELETE'
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Failed to delete project');
            }

            await loadProjects(); // Reload after deletion
            console.log(`Project '${name}' deleted successfully`);
        } catch (err) {
            console.error('Error deleting project:', err);
            error = err.message;
        }
    }

    function confirmDelete(project) {
        console.log("message from confirm delete: Project", project.name); // 👈 This is working
        projectToDelete = project;
        showDeleteDialog = true;
    }

    async function handleConfirmedDelete() {
        console.log("message from handle confirmed delete: Project", projectToDelete.name); // Not working
        if (projectToDelete) {
            await deleteProject(projectToDelete.name);
            showDeleteDialog = false;
            projectToDelete = null;
        }
    }

    function handleCancelDelete() {
        showDeleteDialog = false; // Close the dialog when canceled
    }

    async function openEditDialog(project) {
        currentProject = project;
        editDialogOpen = false; // Force it closed first
        await tick();           // Wait for DOM update cycle
        editDialogOpen = true;  // Now reopen
        console.log(currentProject);
    }

    function handleSave(updatedProject) {
        // Save logic here, such as updating the project in your state or database
        console.log('Save event received in parent:', updatedProject);
        editDialogOpen = false; // Close the dialog after saving
    }
    function handleCancel() {
        editDialogOpen = false; // Close the dialog when canceled
    }




    let openDropdownId = null;

    function toggleDropdown(id) {
        openDropdownId = openDropdownId === id ? null : id;
    }

    function closeDropdown() {
        openDropdownId = null;
    }

    function handleClickOutside(event) {
        if (!event.target.closest('.options-wrapper')) {
            closeDropdown();
        }
    }

    onMount(() => {
        window.addEventListener('click', handleClickOutside);
    });

    function handleProjectClick(project) {
        if (!project.locked) {
            goto('/tool-dashboard');
        }
    }



</script>

<div class="p-6">
    <header class="flex justify-between items-center mb-8">
        <h1 class="text-3xl font-bold">Project Selection</h1>
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
        <!-- Button container -->
        <div class="flex items-center gap-2">
            <button
                    class="bg-[var(--accent)] text-[var(--accent-foreground)] text-sm font-medium px-4 py-2 rounded-md shadow hover:bg-[var(--accent3)]"
                    on:click={openCreateModal}
            >
                Create New Project
            </button>

            <Button
                    on:click={() => showImportModal()}
                    type="button"
                    size="icon"
                    title="Import Project"
                    aria-label="Import Project"
                    class="w-10 h-10 rounded-md bg-[var(--secondary)] text-[var(--muted)] hover:bg-[color:var(--secondary)/90] flex items-center justify-center"
            >
                <Import class="w-5 h-5 text--muted" />
            </Button>
        </div>
    </div>

    {#if isLoading }
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
        <div class="space-y-4">
            <!-- Column Headers -->
            <div class="grid grid-cols-4 px-6 py-2 text-sm font-semibold text-muted-foreground">
                <div>Project Name</div>
                <div>Last Edit</div>
                <div>Lead Analyst</div>
                <div class="text-right pr-4"></div> <!-- delete maybe-->
            </div>


            {#each projects as project (project.id)}
                <div class="grid grid-cols-4 items-center rounded-2xl px-6 py-4 shadow-sm" style="background-color: var(--background1);">
                <!-- Project Info -->
                    <div class="flex items-center gap-4">
                        <!-- Colored status bar -->
                        <div
                                class="w-1.5 h-12 rounded-full"
                                class:bg-green-500={!project.locked}
                                class:bg-red-500={project.locked}
                        ></div>
                        <div>
                            <h3 class="text-base font-semibold text-foreground">{project?.name}</h3>
                        </div>
                    </div>

                    <!-- Last Edit -->
                    <div class="text-sm text-muted-foreground">{project.last_edited || 'N/A'}</div>

                    <!-- Lead Analyst -->
                    <div class="text-sm text-muted-foreground">{analystInitials}</div>

                    <!-- Lock icon + button -->
                    <div class="flex items-center justify-end gap-3">
                        {#if project.locked}
                            <Lock class="w-5 h-5 text-muted-foreground" />
                        {/if}

                        {#if project}
                            <Button
                                    type="button"
                                    class="w-[100px] h-[48px]"
                                    variant="default"
                                    size="lg"
                                    on:click={() => handleProjectClick(project)}
                            >
                                {#if project.locked}
                                    View
                                {:else}
                                    Run Scan
                                {/if}
                            </Button>
                      {/if}
                      
                        <!-- Drop Down: Lock, Delete, and Edit -->
                        <div class="relative options-wrapper">
                            <button
                                    class="options-btn p-1 hover:bg-muted rounded"
                                    on:click|stopPropagation={() => toggleDropdown(project.id)}
                            >
                                <MoreHorizontal class="w-5 h-5" />
                            </button>
                            {#if openDropdownId === project.id}
                                <div class="absolute right-0 mt-2 w-32 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-md shadow-md z-50">
                                    <button
                                            class="flex items-center gap-2 w-full text-left px-4 py-2 text-sm text-muted-foreground hover:bg-gray-100 dark:hover:bg-gray-700"
                                            on:click={() => toggleProjectLock(project.name)}
                                    >
                                        <Lock class="w-4 h-4" />
                                        {project.locked ? 'Unlock' : 'Lock'}
                                    </button>

                                    {#if !project.locked} <!-- Use !project.locked to check when it's unlocked -->
                                        <!-- Add Edit Button -->
                                        <button
                                                class="flex items-center gap-2 w-full text-left px-4 py-2 text-sm text-muted-foreground hover:bg-gray-100 dark:hover:bg-gray-700"
                                                on:click={() =>
                                                {
                                                    openEditDialog(project);
                                                    closeDropdown();
                                                }}
                                        >
                                        <Settings2 class="w-4 h-4" />
                                        Edit
                                        </button>
                                        <button
                                                class="flex items-center gap-2 w-full text-left px-4 py-2 text-sm text-muted-foreground hover:bg-gray-100 dark:hover:bg-gray-700"
                                                on:click={() =>(confirmDelete(project))}
                                        >
                                            <Trash2 class="w-4 h-4" />
                                            Delete
                                        </button>


                                    {/if}
                                </div>
                            {/if}

                        </div>

                    </div>

                </div>
            {/each}
        </div>
    {/if}

    {#if showCreateModal}
        <CreateProjectModal
                analystId={analystId}
                analystInitials={analystInitials}
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

    {#if editDialogOpen}
        <EditProjectDialog
            project={currentProject}
            on:save={handleSave}
            on:cancel={handleCancel}
        />
    {/if}

    <Alert
            isOpen={showDeleteDialog}
            title="Are you absolutely sure?"
            message="This action cannot be undone."
            onCancel={handleCancelDelete}
            onContinue={handleConfirmedDelete}
    />
</div>
