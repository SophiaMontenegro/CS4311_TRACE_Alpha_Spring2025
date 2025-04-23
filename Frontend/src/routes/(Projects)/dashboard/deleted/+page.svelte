<script> //deleted projects page
    import { onMount } from 'svelte';
    import { Trash2, MoreHorizontal, ArchiveRestore, Search  } from 'lucide-svelte';
    import Alert from '$lib/components/ui/alert/Alert.svelte';

    let projects = [];
    let showDeleteDialog = false;
    let projectToDelete = null;
    let showRestoreDialog = false;
    let projectToRestore = null;
    let analystInitials = '';
    let analystId = '';
    let isLoading = true;
    let error = null;
    let openDropdownId = null;

    let searchQuery = '';

    $: filteredProjects = projects.filter(p =>
        p.name.toLowerCase().includes(searchQuery.toLowerCase())
    );


    onMount(async () => {
        analystInitials = localStorage.getItem('analyst_initials') || '';
        analystId = localStorage.getItem('analyst_id') || '';

        if (!analystInitials || !analystId) {
            window.location.href = '/login';
            return;
        }

        await loadProjects();
    });

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

    async function loadProjects() {
        isLoading = true;
        error = null;

        try {
            const response = await fetch(`http://127.0.0.1:8000/team3/projects_deleted/analyst/${analystId}`);
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

    function handleLogout() {
        localStorage.removeItem('analyst_id');
        localStorage.removeItem('analyst_initials');
        window.location.href = '/login';
    }

    function confirmDelete(project) {
        projectToDelete = project;
        showDeleteDialog = true;
    }

    async function deleteProject(name) {
        if (!projectToDelete) return;

        try {
            const response = await fetch(`http://127.0.0.1:8000/team3/projects/${encodeURIComponent(name)}/permanently_delete?analyst_initials=${analystInitials}`, {
                method: 'PUT'
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Failed to Permanently Delete Project');
            }

            await loadProjects(); // Refresh projects list
        } catch (err) {
            console.error('Error permanently deleting project', err);
            error = err.message;
        }

        // Remove it from local list
        projects = projects.filter(p => p.id !== projectToDelete.id); // may not be necessary
        showDeleteDialog = false;
        projectToDelete = null;
    }

    function handleCancelDelete() {
        showDeleteDialog = false;
        projectToDelete = null;
    }

    async function handleConfirmedDelete() {
        console.log("message from handle confirmed delete: Project", projectToDelete.name); // Not working
        if (projectToDelete) {
            await deleteProject(projectToDelete.name);
            showDeleteDialog = false;
            projectToDelete = null;
        }
    }

    function confirmRestore(project) {
        projectToRestore = project;
        showRestoreDialog = true;
    }

    async function restoreProject(name) {
        if (!projectToRestore) return;
        try {
            const response = await fetch(`http://127.0.0.1:8000/team3/projects/${encodeURIComponent(name)}/restore?analyst_initials=${analystInitials}`, {
                method: 'PUT'
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Failed to restore project', projectToRestore);
            }

            await loadProjects(); // Refresh projects list
        } catch (err) {
            console.error('Error restoring project:', err);
            error = err.message;
        }

        // Remove it from local list
        projects = projects.filter(p => p.id !== projectToRestore.id); // may not need
        showRestoreDialog = false;
        projectToRestore = null;
    }

    function handleCancelRestore() {
        showRestoreDialog = false;
        projectToRestore = null;
    }

    async function handleConfirmedRestore() {
        console.log("message from handle confirmed restore: Project", projectToRestore.name); // Not working
        if (projectToRestore) {
            await restoreProject(projectToRestore.name);
            showRestoreDialog = false;
            projectToRestore = null;
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
        <h2 class="text-2xl font-semibold">Deleted Projects</h2>
        <!-- Add search bar -->
        <div
                class="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-gray-300 text-sm"
                style="background-color: var(--background1); max-width: 300px;"
        >
            <Search class="w-4 h-4 text-muted-foreground" />
            <input
                    type="text"
                    placeholder="Search projects"
                    bind:value={searchQuery}
                    class="w-full bg-transparent outline-none text-sm placeholder:text-muted-foreground"
            />
        </div>


    </div>

    {#if isLoading }
        <div class="text-gray-500">Loading deleted projects...</div>
    {:else if error}
        <div class="text-red-500">Error: {error}</div>
    {:else if projects.length === 0}
        <div class="text-center mt-12 space-y-4">
            No Projects Deleted
        </div>
    {:else}
        <div class="space-y-4">
            <!-- Column Headers -->
            <div class="grid grid-cols-[1fr_1fr_1fr_auto] px-6 py-2 text-sm font-semibold text-muted-foreground">
                <div>Project Name</div>
                <div>Last Edited</div>
                <div>Lead Analyst</div>
                <div class="text-right pr-4"></div> <!-- aligns with dropdown -->
            </div>

            {#each filteredProjects as project (project.id)}
                <div class="grid grid-cols-[1fr_1fr_1fr_auto] items-center rounded-2xl px-6 py-4 shadow-sm" style="background-color: var(--background1);">
                    <!-- Project Name -->
                    <div class="text-sm font-medium">{project.name}</div>

                    <!-- Last Edited -->
                    <div class="text-sm text-muted-foreground">{project.last_edited || 'N/A'}</div>

                    <!-- Lead Analyst -->
                    <div class="text-sm text-muted-foreground">{analystInitials}</div>

                    <!-- Dropdown Button -->
                    <div class="relative justify-self-end">
                        <button
                                class="p-1 hover:bg-muted rounded"
                                on:click|stopPropagation={() => toggleDropdown(project.id)}
                        >
                            <MoreHorizontal class="w-5 h-5" />
                        </button>
                        {#if openDropdownId === project.id}
                            <div class="absolute right-0 bottom-full mb-2 w-32 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-md shadow-md z-50">
                            <button
                                        class="flex items-center gap-2 w-full text-left px-4 py-2 text-sm text-muted-foreground hover:bg-gray-100 dark:hover:bg-gray-700"
                                        on:click={() => confirmRestore(project)}
                                >
                                    <ArchiveRestore class="w-4 h-4" />
                                    Restore
                                </button>
                                <button
                                        class="flex items-center gap-2 w-full text-left px-4 py-2 text-sm text-muted-foreground hover:bg-gray-100 dark:hover:bg-gray-700"
                                        on:click={() => confirmDelete(project)}
                                >
                                    <Trash2 class="w-4 h-4" />
                                    Delete
                                </button>
                            </div>
                        {/if}
                    </div>
                </div>
            {/each}

        </div>
    {/if}

    <Alert
            isOpen={showDeleteDialog}
            title="Are you sure you want to delete the project forever?"
            message="This action cannot be undone."
            onCancel={handleCancelDelete}
            onContinue={handleConfirmedDelete}
    />
    <Alert
            isOpen={showRestoreDialog}
            title="Are you sure you want to restore the project forever?"
            message="Check Project tab after restoration."
            onCancel={handleCancelRestore}
            onContinue={handleConfirmedRestore}
    />
</div>

