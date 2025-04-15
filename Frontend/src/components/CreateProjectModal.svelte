<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    //import { X, CalendarIcon, UploadCloud, Trash2, UserPlus, Mail } from "lucide-svelte";
    import { Input } from '../../../components/ui/input';
    import { Textarea } from '../../../components/ui/textarea';
    import { Button } from '../../../components/ui/button';


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

    let errors = {
        projectName: '',
        dates: ''
    };

    function handleFileUpload(event: Event) {
        const input = event.target as HTMLInputElement;
        if (input.files) {
            files = [...files, ...Array.from(input.files)];
        }
    }

    function removeFile(index: number) {
        files.splice(index, 1);
        files = [...files];
    }

    function validateForm(): boolean {
        let valid = true;
        errors = { projectName: '', dates: '' };

        if (!projectName.trim()) {
            errors.projectName = 'Project name is required';
            valid = false;
        }

        if (!startDate) {
            errors.dates = 'Start date is required';
            valid = false;
        } else if (!endDate) {
            errors.dates = 'End date is required';
            valid = false;
        } else if (new Date(endDate) < new Date(startDate)) {
            errors.dates = 'End date must be after start date';
            valid = false;
        }

        return valid;
    }

    function addUser() {
        const trimmed = newUser.trim();
        if (trimmed && !userList.includes(trimmed)) {
            userList = [...userList, trimmed];
            newUser = '';
        }
    }

    function removeUser(index: number) {
        userList.splice(index, 1);
        userList = [...userList];
    }

    function handleSubmit() {
        if (validateForm()) {
            const projectData = {
                projectName,
                description,
                startDate,
                endDate,
                userList,
                analystId,
                analystInitials
            };

            console.log('Submitting project data:', projectData);
            dispatch('create', projectData);
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
                <Input bind:value={projectName} placeholder="Enter project name" />
                {#if errors.projectName}
                    <p class="text-red-500 text-sm">{errors.projectName}</p>
                {/if}
            </div>

            <!-- Start Date -->
            <div class="space-y-2">
                <label class="text-sm font-medium">Start Date *</label>
                <div class="relative">
                    <Input type="date" bind:value={startDate} class="pr-10" />
                    <CalendarIcon class="absolute right-3 top-2.5 w-5 h-5 text-muted-foreground" />
                </div>
            </div>

            <!--
            <div class="space-y-2">
                <label class="text-sm font-medium">Time *</label>
                <div class="relative">
                    <Input type="time" bind:value={time} class="pr-10" />
                    <Clock class="absolute right-3 top-2.5 w-5 h-5 text-muted-foreground" />
                </div>
            </div>
            Time -->

            <!-- Project Description -->
            <div class="space-y-2 md:col-span-2">
                <label class="text-sm font-medium">Project Description</label>
                <Textarea bind:value={description} class="h-24" placeholder="Enter project description" />
            </div>

            <!-- Upload Files -->
            <div class="space-y-2 md:col-span-2">
                <label class="text-sm font-medium">Upload NMap</label>
                <Input type="file" multiple on:change={handleFileUpload} />
                <div class="space-y-1 mt-2">
                    {#each files as file, index}
                        <div class="flex items-center justify-between bg-muted px-3 py-2 rounded-md text-sm">
                            <div class="flex items-center gap-2">
                                <Check class="w-4 h-4 text-green-500" />
                                <span>{file.name}</span>
                            </div>
                            <button type="button" on:click={() => removeFile(index)}>
                                <Trash2 class="w-4 h-4 text-destructive" />
                            </button>
                        </div>
                    {/each}
                </div>
            </div>

            <!-- Team Members -->
            <div class="space-y-2 md:col-span-2">
                <label class="text-sm font-medium">Team Members</label>
                <div class="flex gap-2">
                    <Input bind:value={newUser} placeholder="Enter initials" />
                    <Button size="sm" on:click={addUser}>
                        <UserPlus class="w-4 h-4 mr-1" /> Add
                    </Button>
                </div>
                <ul class="space-y-1 mt-2">
                    {#each userList as user, i}
                        <li class="flex items-center justify-between bg-muted px-3 py-2 rounded-md text-sm">
                            <span><Mail class="inline-block w-4 h-4 mr-1" /> {user}</span>
                            <button type="button" on:click={() => removeUser(i)}>
                                <Trash2 class="w-4 h-4 text-destructive" />
                            </button>
                        </li>
                    {/each}
                </ul>
            </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex justify-end gap-2">
            <Button variant="ghost" size="sm" on:click={handleClose}>Cancel</Button>
            <Button variant="default" size="sm" on:click={handleSubmit}>Create</Button>
        </div>
    </div>
</div>
