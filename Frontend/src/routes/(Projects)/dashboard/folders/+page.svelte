<script>
    import { onMount, tick } from 'svelte';
    import { goto } from '$app/navigation';
    import { Lock } from 'lucide-svelte';
    import { Button } from '$lib/components/ui/button';

    let projects = [];
    let isLoading = true;
    let error = null;
    let analystInitials = '';
    let analystId = '';


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
            const response = await fetch(`http://127.0.0.1:8000/team3/projects/analyst/${analystId}`); //edit this please to have projects the user is a part of NOT owns
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
        <h2 class="text-2xl font-semibold">Shared Projects</h2>
    </div>

    {#if isLoading }
        <div class="text-gray-500">Loading projects...</div>
    {:else if error}
        <div class="text-red-500">Error: {error}</div>
    {:else if projects.length === 0}
        <div class="text-center mt-12 space-y-4">
            <p class="text-lg">You don't have any projects you are a part of.</p>

        </div>
    {:else}
        <div class="space-y-4">
            <!-- Column Headers -->
            <div class="grid grid-cols-4 px-6 py-2 text-sm font-semibold text-muted-foreground">
                <div>Project Name</div>
                <div>Last Edit</div>
                <div>Lead Analyst</div>
                <div>Port</div>
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
                    <div class="text-sm text-muted-foreground">{project.timestamp || 'N/A'}</div>

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
                                    Join
                                {/if}
                            </Button>
                        {/if}

                    </div>

                </div>
            {/each}
        </div>
    {/if}

</div>
