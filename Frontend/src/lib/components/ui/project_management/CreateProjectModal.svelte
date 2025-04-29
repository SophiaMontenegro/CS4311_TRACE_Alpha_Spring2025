<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    //import { X, CalendarIcon, UploadCloud, Trash2, UserPlus, Mail } from "lucide-svelte";
    import { Input } from '../input';
    import { Textarea } from '../textarea';
    import { Button } from '../button';


    import { CalendarIcon, Clock, Mail, Trash2, Check, UserPlus, X } from 'lucide-svelte';

    export let analystId: string = '';
    export let analystInitials: string = '';

    const dispatch = createEventDispatcher();

    const formatDate = (date: Date): string => date.toISOString().split('T')[0];

    let projectName = '';
    let startDate = formatDate(new Date());
    let endDate = formatDate(new Date(Date.now() + 30 * 24 * 60 * 60 * 1000));
    let description = '';
    let files: File[] = [];

    let userList: string[] = [];
    let newUser = '';
    let userError = '';
    let isVerifying = false;

    let directoryPath: string = '';
    let lead_ip: string = '';


    let errors = {
        projectName: '',
        startDate: '',
        endDate: '',
        saveDirectory: '',
        lead_ip: ''
    };

    function removeFile(index: number) {
        files.splice(index, 1);
        files = [...files];
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
        errors = { ...errors, projectName: '', startDate: '', endDate: '', saveDirectory: '', lead_ip: '' };

        const trimmedName = projectName.trim();

        if (!trimmedName) {
            errors.projectName = 'Project name is required.';
            valid = false;
        } else {
            const verify_name = await check_name(trimmedName); // ✅ await async call

            if (verify_name === false) {
                errors.projectName = 'Project name already exists.';
                valid = false;
            }
        }

        if (!startDate) {
            errors.startDate = 'Start date is required.';
            valid = false;
        } else if (!endDate) {
            errors.endDate = 'End date is required.';
            valid = false;
        } else if (new Date(endDate) < new Date(startDate)) {
            errors.startDate = 'End date must be after start date.';
            valid = false;
        }

        const trimmedPath = directoryPath.trim();
        console.log("PATH boolean: ", !trimmedPath);
        if (!trimmedPath) {
            errors.saveDirectory = 'Directory needs to be added.';
            valid = false;
        }
        else {
            const valid_path= await verifyPath(trimmedPath); // ✅ await async call
            if (valid_path === false) {
                errors.saveDirectory = 'Directory is invalid';
                valid = false;
            }
        }
        const ipRegex = /^(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}$/;
        if (!lead_ip) {
            errors.lead_ip = 'Lead IP address is required.';
            valid = false;
        } else if (!ipRegex.test(lead_ip)) {
            errors.lead_ip = 'Invalid Lead IP address.';
            valid = false;
        }

        return valid;
    }

    async function verifyPath(path) {
        try {
            const response = await fetch('http://127.0.0.1:8000/team3/directory_path_verify/', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    directory_path: path
                })
            });

            const responseData = await response.json();

            if (!response.ok) {
                let errorMessage = 'Failed to verify path';
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
            if (responseData.status === "invalid") {
                return false;
            }

            return true;
        } catch (err) {
            console.error("verify path error:", err);
            return false;
        }
    }

    async function addUser() {
        const trimmed = newUser.trim().toUpperCase();
        userError = '';

        if (!trimmed) return; // empty

        // Check if already added
        if (userList.includes(trimmed)) {
            userError = `User "${trimmed}" is already added.`;
            return;
        }
        // Check if trying to add self
        if (analystInitials === trimmed) {
            userError = `User "${trimmed}" is yourself.`;
            return;
        }

        isVerifying = true;

        try {
            const response = await fetch(`http://127.0.0.1:8000/team3/analysts/verify`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ initials: trimmed }),
            });

            if (!response.ok) {
                userError = `User "${trimmed}" is not valid.`;
                return;
            }

            const data = await response.json();

            // Assuming your backend returns { valid: true/false }
            if (data.analyst_id) {
                newUser = '';
            } else {
                userError = `User "${trimmed}" is not valid.`;
            }

        } catch (error) {
            userError = `Network error: ${error.message}`;
        } finally {
            isVerifying = false;
        }
    }

    function removeUser(index: number) {
        userList.splice(index, 1);
        userList = [...userList];
    }

    async function handleSubmit() {
        const isValid = await validateForm();

        if (isValid) {
            const projectData = {
                projectName,
                description,
                startDate,
                endDate,
                userList,
                lead_ip,
                directoryPath,
                analystId,
                analystInitials
            };

            dispatch('create', projectData);
            handleClose();
        }
    }

    function handleClose() {
        dispatch('close');
    }
</script>

<div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
    <div class="bg-white dark:bg-background rounded-2xl shadow-xl w-full max-w-3xl p-6 space-y-6">

        <!-- Modal Header -->
        <div class="flex justify-between items-center">
            <h2 class="text-xl font-semibold">Create Project</h2>
            <button class="text-gray-500 hover:text-gray-700" on:click={handleClose}>
                <X class="w-5 h-5" />
            </button>
        </div>

        <!-- Form Fields -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">

            <!-- Project Name -->
            <div class="space-y-2">
                <label class="text-sm font-medium">Project Name *</label>
                <Input type="text" class="input-class" bind:value={projectName} placeholder="Enter project name" />
                {#if errors.projectName}
                    <p class="text-red-500 text-sm">{errors.projectName}</p>
                {/if}
            </div>

            <!-- Start & End Dates in same row -->
            <div class="col-span-2 grid grid-cols-1 md:grid-cols-2 gap-4">
                <!-- Start Date -->
                <div class="space-y-2">
                    <label class="text-sm font-medium">Start Date *</label>
                    <div class="relative">
                        <Input type="date" bind:value={startDate} class="pr-10" />

                    </div>
                    {#if errors.startDate}
                        <p class="text-red-500 text-sm">{errors.startDate}</p>
                    {/if}
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
            </div>



            <!-- Project Description -->
            <div class="space-y-2 md:col-span-2">
                <label class="text-sm font-medium">Project Description</label>
                <Textarea bind:value={description} class="h-24" placeholder="Enter project description" />
            </div>

            <!-- Lead IP Address -->
            <div class="space-y-2 md:col-span-2">
                <label class="text-sm font-medium">Lead IP *</label>
                <Input type="text" class="input-class" bind:value={lead_ip} placeholder="Enter lead IP address" />
                {#if errors.lead_ip}
                    <p class="text-red-500 text-sm">{errors.lead_ip}</p>
                {/if}
            </div>
            <!-- Save Directory Selection -->
            <div class="space-y-2 md:col-span-2">
                <label class="text-sm font-medium">Save Directory Path *</label>

                <Input
                        type="text"
                        class="input-class"
                        placeholder="Enter full directory path..."
                        bind:value={directoryPath}
                />

                {#if directoryPath}
                    <div class="space-y-1 mt-2">
                        <div class="flex items-center justify-between bg-muted px-3 py-2 rounded-md text-sm">
                            <div class="flex items-center gap-2">
                                <Check class="w-4 h-4 text-green-500" />
                                <span class="break-all">{directoryPath}</span>
                            </div>
                            <button type="button" on:click={() => (directoryPath = '')}>
                                <Trash2 class="w-4 h-4 text-destructive" />
                            </button>
                        </div>
                    </div>
                {/if}
                {#if errors.saveDirectory}
                    <p class="text-red-500 text-sm">{errors.saveDirectory}</p>
                {/if}
            </div>




            <!-- Team Members -->
            <div class="space-y-2 md:col-span-2">
                <label class="text-sm font-medium">Team Members</label>
                <div class="flex gap-2">
                    <Input type="text" class="input-class" bind:value={newUser} placeholder="Enter initials" />
                    <button class="flex items-center bg-[var(--accent)] text-[var(--accent-foreground)] text-sm font-small px-4 py-2 rounded-md shadow hover:bg-[var(--accent3)]"
                            on:click={addUser}>
                        <UserPlus class="w-4 h-4 mr-1" /> Add
                    </button>
                </div>
                <div class="flex flex-wrap gap-2 mt-2">
                    {#each userList as user, i}
                        <div class="flex items-center bg-muted text-sm px-3 py-1 rounded-full">
                            <div class="w-6 h-6 rounded-full bg-primary text-white flex items-center justify-center mr-2 text-xs font-bold">
                                {user}
                            </div>
                            <button type="button" on:click={() => removeUser(i)} class="text-gray-500 hover:text-red-500 ml-1">
                                <X class="w-4 h-4" />
                            </button>
                        </div>
                    {/each}
                </div>
            </div>
        </div>

        {#if userError}
            <p class="text-sm text-red-500 mt-2">{userError}</p>
        {/if}

        {#if isVerifying}
            <p class="text-sm text-gray-500 mt-2">Verifying...</p>
        {/if}

        <!-- Action Buttons -->
        <div class="flex justify-end gap-2">
            <Button class="btn-class" variant="ghost" size="sm" onclick={handleClose}>Cancel</Button>
            <!-- Not in a form -->
            <Button class="btn-class" variant="default" size="sm" onclick={async () => {
                await handleSubmit();
            }}>
                Create
            </Button>


        </div>
    </div>
</div>
