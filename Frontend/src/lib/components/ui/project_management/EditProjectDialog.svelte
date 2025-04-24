<script lang="ts">
    import { onMount } from 'svelte';
    import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '$lib/components/ui/dialog/index.js';
    import { Button } from '$lib/components/ui/button/index.js';
    import { Input } from '$lib/components/ui/input/index.js';
    import { Textarea } from '$lib/components/ui/textarea/index.js';
    import { createEventDispatcher} from 'svelte';
    import { UserPlus, X, Loader2  } from 'lucide-svelte';

    export let project;
    export let analystInitials: string = '';
    const dispatch = createEventDispatcher();
    let modalOpen = true;

    let name = '';
    let endDate = '';
    let description = '';

    let userList = [];
    let newUser = ''; //for manually added analysts
    let currentAnalysts = []; //fetched form backend
    let userError = '';
    let isVerifying = false

    let projectName = ''; // updated

    let errors = {
        projectName: '',
        endDate: ''
    };

    console.log("EditProjectDialog mounted"); // ✅ Check this!

    onMount(async () => {
        name = project.name;
        endDate = project.end_date || '';
        description = project.description || '';
        await show_analysts()
        userList = [...currentAnalysts]; // ← Sync with fetched data!
    });


    async function show_analysts() {
        try {
            const response = await fetch(`http://127.0.0.1:8000/team3/projects/get_analyst/${project.name}`);
            if (response.ok) {
                const data = await response.json();
                currentAnalysts = data.analysts || [];
                userList = [...currentAnalysts]; // ← Populate userList from backend
            } else {
                console.error("Failed to fetch analysts");
            }
        } catch (err) {
            console.error("Error fetching analysts:", err);
        }
    }

    async function addUser() {
        const trimmed = newUser.trim().toUpperCase();
        userError = '';

        console.log("here is: ", trimmed);

        if (!trimmed) return;

        if (userList.includes(trimmed)) {
            userError = `User "${trimmed}" is already added.`;
            return;
        }

        console.log("boolean ", analystInitials === trimmed);
        console.log("lead ", analystInitials);

        if (analystInitials === trimmed) {
            userError = `You cannot add yourself ("${trimmed}").`;
            return;
        }

        isVerifying = true;

        try {
            // First, verify the user exists
            const verifyResponse = await fetch(`http://127.0.0.1:8000/team3/analysts/verify`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ initials: trimmed }),
            });

            if (!verifyResponse.ok) {
                userError = `User "${trimmed}" is not valid.`;
                return;
            }

            // Add the user to the project
            const addResponse = await fetch(`http://127.0.0.1:8000/team3/projects/${project.name}/member_added?new_user=${trimmed}&lead_analyst=${analystInitials}`, {
                method: 'PUT',
            });

            if (!addResponse.ok) {
                const errData = await addResponse.json();
                userError = errData.detail || `Failed to add user "${trimmed}".`;
                return;
            }

            userList = [...userList, trimmed];
            newUser = '';

        } catch (err) {
            userError = `Network error: ${err.message}`;
        } finally {
            isVerifying = false;
        }
        await show_analysts(); // reload
    }


    async function removeUser(user, index) {
        //const user = userList[index];
        try {
            const res = await fetch(`http://127.0.0.1:8000/team3/projects/${project.name}/member_removed?new_user=${user}&lead_analyst=${analystInitials}`, {
                method: 'PUT',
            });

            if (!res.ok) {
                const errData = await res.json();
                console.error('Failed to remove:', errData);
                return;
            }

            userList.splice(index, 1);
        } catch (err) {
            console.error('Error removing user:', err.message);
        }
        await show_analysts(); // reload
    }

    async function check_name(name) {

        try {
            const response = await fetch('http://127.0.0.1:8000/team3/project_name/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    project_name: name,
                    analyst_initials: analystInitials,
                })
            });

            const responseData = await response.json();

            if (!response.ok) {
                let errorMessage = 'Failed to verify project name';
                if (responseData.detail) {
                    errorMessage = typeof responseData.detail === 'string'
                        ? responseData.detail
                        : JSON.stringify(responseData.detail);
                } else if (typeof responseData === 'object') {
                    errorMessage = JSON.stringify(responseData);
                }

                throw new Error(errorMessage);
            }

            // Check if name is taken
            if (responseData.status === "taken") {
                return false;
            }

            return true;
        } catch (err) {
            console.error("check_name error:", err);
            return false;
        }
    }

    async function validateForm(): boolean {
        let valid = true;
        // Force a reactive reset
        errors = { ...errors, projectName: '', startDate: '', endDate: '', saveDirectory: '' };

        const trimmedName = projectName.trim();

        if (!trimmedName) {
            errors.projectName = 'Project name is required';
            valid = false;
        } else {
            const verify_name = await check_name(trimmedName); // ✅ await async call

            if (verify_name === false) {
                errors.projectName = 'Project name already exists';
                valid = false;
            }
        }

        if (!endDate) {
            errors.endDate = 'End date is required';
            valid = false;
        } else if (new Date(endDate) < new Date(project.start_date)) {
            errors.endDate = 'End date must be after start date';
            valid = false;
        }


        return valid;
    }




    async function handleSave() {
        console.log('Saving project:', project);
        const verify = await validateForm();

        if(verify){
            // save project name

            // save project description

            //save project end date
        }
    }

    async function handleCancel() {
        dispatch('cancel');
        //modalOpen = false;
    }
</script>

<Dialog open={true}>
    <DialogContent class="max-w-lg z-[100]">
        <DialogHeader>
            <DialogTitle>Edit Project</DialogTitle>
        </DialogHeader>

        <!-- Project Name -->
        <div class="space-y-2">
            <label class="text-sm font-medium">Project Name *</label>
            <Input type="text" class="input-class" bind:value={projectName} placeholder={name} />
            {#if errors.projectName}
                <p class="text-red-500 text-sm">{errors.projectName}</p>
            {/if}
        </div>

        <!-- Project Description -->
        <div class="space-y-2 md:col-span-2">
            <label class="text-sm font-medium">Project Description</label>
            <Textarea bind:value={description} class="h-24" placeholder={description} />
        </div>

        <!-- End Date -->
        <div class="space-y-2">
            <label class="text-sm font-medium">End Date *</label>
            <div class="relative">
                <Input type="date" bind:value={endDate} class="pr-10" />

            </div>
            {#if errors.endDate}
                <p class="text-red-500 text-sm">{errors.endDate}</p>
            {/if}
        </div>

        <div class="mt-4">
            <div class="mb-2 font-semibold">Add Analysts</div>

            <!-- Input + Button -->
            <div class="flex gap-2 items-center">
                <Input
                        type="text"
                        class="input-class"
                        bind:value={newUser}
                        placeholder="Enter initials"
                        disabled={isVerifying}
                />
                <button
                        class="flex items-center bg-[var(--accent)] text-[var(--accent-foreground)] text-sm font-medium px-4 py-2 rounded-md shadow hover:bg-[var(--accent3)] disabled:opacity-60 disabled:cursor-not-allowed"
                        on:click={addUser}
                        disabled={isVerifying}
                >
                    {#if isVerifying}
                        <Loader2 class="w-4 h-4 mr-1 animate-spin" />
                    {:else}
                        <UserPlus class="w-4 h-4 mr-1" />
                    {/if}
                    Add
                </button>
            </div>

            <!-- Error Message -->
            {#if userError}
                <div class="text-red-500 text-sm mt-1">{userError}</div>
            {/if}

            <!-- User Tags -->
            <div class="flex flex-wrap gap-2 mt-2">
                {#each userList as user, i}
                    <div class="flex items-center bg-muted text-sm px-3 py-1 rounded-full">
                        <div class="w-6 h-6 rounded-full bg-primary text-white flex items-center justify-center mr-2 text-xs font-bold">
                            {user}
                        </div>
                        <button
                                type="button"
                                on:click={() => removeUser(user, i)}
                                class="text-gray-500 hover:text-red-500 ml-1"
                        >
                            <X class="w-4 h-4" />
                        </button>
                    </div>
                {/each}
            </div>
        </div>


        <DialogFooter>
            <Button onclick={() => handleSave()}>Save</Button>
            <Button variant="outline" onclick={handleCancel}>Cancel</Button>
        </DialogFooter>
    </DialogContent>
</Dialog>
