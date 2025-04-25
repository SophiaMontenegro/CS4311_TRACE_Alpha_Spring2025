<script lang="ts">
    import { onMount } from 'svelte';
    import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '$lib/components/ui/dialog/index.js';
    import { Button } from '$lib/components/ui/button/index.js';
    import { Input } from '$lib/components/ui/input/index.js';
    import { Textarea } from '$lib/components/ui/textarea/index.js';
    import { createEventDispatcher} from 'svelte';
    import { UserPlus, X, Loader2  } from 'lucide-svelte';
    import Alert from '$lib/components/ui/alert/Alert.svelte';

    export let project;
    export let analystInitials: string = '';
    const dispatch = createEventDispatcher();
    let modalOpen = true;

    let name = ''; // actual name
    let og_endDate = '';
    let og_description = '';

    let userList = [];
    let newUser = ''; //for manually added analysts
    let currentAnalysts = []; //fetched form backend
    let userError = '';
    let isVerifying = false

    let projectName = ''; // updated
    let new_description = '';
    let new_endDate = '';
    let projectName_error = '';
    let endDate_error = '';

    let og_port = '';
    let new_port = ''; // default to existing port
    let port_error = '';



    console.log("EditProjectDialog mounted"); // ✅ Check this!

    onMount(async () => {
        name = project.name;
        og_endDate = project.end_date || '';
        new_endDate = formatDateToInput(og_endDate); // <- formatted for input
        og_description = project.description || '';
        og_port = project.port;
        new_port = project.port || '';
        await show_analysts()
        userList = [...currentAnalysts]; // ← Sync with fetched data!
    });

    function formatDateToInput(dateStr: string) {
        const date = new Date(dateStr);
        if (isNaN(date.getTime())) return '';
        return date.toISOString().split('T')[0]; // Gets YYYY-MM-DD
    }


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
        endDate_error = '';

        if (!new_endDate) {
            endDate_error = 'End date is required';
            valid = false;
        } else if (new Date(new_endDate) < new Date(project.start_date)) {
            endDate_error = 'End date must be after start date';
            valid = false;
        }

        if (!new_port) {
            port_error = 'Port number is required';
            valid = false;
        } else if (isNaN(Number(new_port)) || Number(new_port) < 1 || Number(new_port) > 65535) {
            port_error = 'Invalid port number';
            valid = false;
        }

        return valid;
    }

    async function changeProjectName() {
        // Force a reactive reset
        isVerifying = true
        projectName_error = '';
        const trimmedName = projectName.trim();

        if (trimmedName === name){
            projectName_error = 'Project name is the same';
            return;
        }

        if (!trimmedName) {
            projectName_error = 'Project name is required';
            return;

        } else {
            const verify_name = await check_name(trimmedName); // ✅ await async call

            if (verify_name === false) {
                projectName_error = 'Project name already exists';
                return;
            }
        }
        try {
            const baseURL = 'http://127.0.0.1:8000/team3';

            const resName = await fetch(`${baseURL}/projects/${name}/name?new_name=${trimmedName}&analyst_name=${analystInitials}`, {
                method: 'PUT'
            });
            if (!resName.ok) {
                throw new Error('Failed to update project name');
                return;
            }


        } catch (err) {
            console.error(err);
            return;
        } finally {
            isVerifying = false;
        }

        name = projectName; //change the name in the frontend
        console.log("Changed project name: ", name);

    }




    async function handleSave() {
        console.log('Saving project:', project);
        const verify = await validateForm();

        if (!verify) return; // NOT VALID

        try {
            const baseURL = 'http://127.0.0.1:8000/team3';

            //  Update Description
            if (new_description !== og_description) {
                const resDesc = await fetch(`${baseURL}/projects/${encodeURIComponent(name)}/description?description=${encodeURIComponent(new_description)}&analyst_name=${analystInitials}`, {
                    method: 'PUT'
                });
                if (!resDesc.ok) throw new Error('Failed to update description');
            }

            // Update End Date
            if (new_endDate !== og_endDate) {
                const resDate = await fetch(`${baseURL}/projects/${encodeURIComponent(name)}/timeline?end_date=${new_endDate}&analyst_name=${analystInitials}`, {
                    method: 'PUT'
                });
                if (!resDate.ok) throw new Error('Failed to update end date');
            }

            // Update Port Number
            if (new_port !== String(project.port)) {
                const resPort = await fetch(`${baseURL}/projects/${encodeURIComponent(name)}/port?port=${new_port}&analyst_name=${analystInitials}`, {
                    method: 'PUT'
                });
                if (!resPort.ok) throw new Error('Failed to update port number');
            }

            const update_last_edited = await fetch(`${baseURL}/projects/${encodeURIComponent(name)}/last_edited`, {
                method: 'PUT'
            });
            if (!update_last_edited.ok) throw new Error('Failed to update last edited');

            alert("Project updated successfully!");
        } catch (err) {
            console.error(err);
            alert("There was a problem saving the project.");
        }
        dispatch('save');
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

        <!-- Form Fields Stack -->
        <div class="space-y-4">
            <!-- Project Name -->
            <!-- Project Name -->
            <div class="space-y-2">
                <label class="text-sm font-medium">Project Name *</label>

                <!-- Input + Button wrapper -->
                <div class="flex gap-2">
                    <Input
                            type="text"
                            class="input-class flex-1"
                            bind:value={projectName}
                            placeholder={name}
                    />
                    <button
                            class="flex items-center bg-[var(--accent)] text-[var(--accent-foreground)] text-sm font-medium px-4 py-2 rounded-md shadow hover:bg-[var(--accent3)] disabled:opacity-60 disabled:cursor-not-allowed"
                            on:click={changeProjectName}
                            disabled={isVerifying}
                    >
                        {#if isVerifying}
                            <Loader2 class="w-4 h-4 mr-1 animate-spin" />
                        {:else}
                        Change
                        {/if}
                    </button>
                </div>

                {#if projectName_error}
                    <p class="text-red-500 text-sm">{projectName_error}</p>
                {/if}
            </div>


            <!-- Project Description -->
            <div class="space-y-2">
                <label class="text-sm font-medium">Project Description</label>
                <Textarea bind:value={new_description} class="h-24" placeholder={og_description} />
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <!-- End Date -->
                <div class="space-y-2">
                    <label class="text-sm font-medium">End Date *</label>
                    <Input type="date" bind:value={new_endDate} />
                    {#if endDate_error}
                        <p class="text-red-500 text-sm">{endDate_error}</p>
                    {/if}
                </div>

                <!-- Port Number -->
                <div class="space-y-2">
                    <label class="text-sm font-medium">Port Number *</label>
                    <Input type="number" bind:value={new_port} min="1" max="65535" />
                    {#if port_error}
                        <p class="text-red-500 text-sm">{port_error}</p>
                    {/if}
                </div>
            </div>


            <!-- Add Analysts Section -->
            <div class="space-y-2">
                <div class="font-semibold">Add Analysts</div>

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
                    <div class="text-red-500 text-sm">{userError}</div>
                {/if}

                <!-- User Tags -->
                <div class="flex flex-wrap gap-2">
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
        </div>

        <!-- Footer Buttons -->
        <DialogFooter class="mt-6">
            <button
                    variant="outline" on:click={handleCancel}>Cancel</button>
            <button class="flex items-center bg-[var(--accent)] text-[var(--accent-foreground)] text-sm font-medium px-4 py-2 rounded-md shadow hover:bg-[var(--accent3)] disabled:opacity-60 disabled:cursor-not-allowed"
                    on:click={handleSave}>
                Save
            </button>
        </DialogFooter>
    </DialogContent>
</Dialog>

<Alert
        isOpen={showSave}
        title="Are you absolutely sure?"
        message="This action cannot be undone."
        onCancel={handleCancelDelete}
        onContinue={handleConfirmedDelete}
/>
