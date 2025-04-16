<script>
    import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '$lib/components/ui/dialog/index.js';
    import { Button } from '$lib/components/ui/button/index.js';
    import { Input } from '$lib/components/ui/input/index.js';
    import { Textarea } from '$lib/components/ui/textarea/index.js';
    import { createEventDispatcher, onMount } from 'svelte';

    export let project;
    const dispatch = createEventDispatcher();
    let modalOpen = true;

    let name = '';
    let endDate = '';
    let description = '';
    let users = [];
    let newUser = '';

    console.log("EditProjectDialog mounted"); // ✅ Check this!

    onMount(() => {
        name = project.name;
        endDate = project.endDate || '';
        description = project.description || '';
        users = [...(project.users || [])];
    });

    function addUser() {
        if (newUser.trim()) {
            users = [...users, newUser.trim()];
            newUser = '';
        }
    }

    function removeUser(index) {
        users.splice(index, 1);
    }

    async function handleSave() {
        console.log('Saving project:', project);
        dispatch('save', {
            ...project,
            name,
            endDate,
            description,
            users
        });
        //modalOpen = false;
    }

    async function handleCancel() {
        dispatch('cancel');
        //modalOpen = false;
    }
</script>

<Dialog open={true}>
    <DialogContent class="max-w-lg">
        <DialogHeader>
            <DialogTitle>Edit Project</DialogTitle>
        </DialogHeader>

        <div class="space-y-4">
            Project Name:
            <Input bind:value={name} placeholder="Project Name" />
            End Date:
            <Input bind:value={endDate} type="date"  placeholder="End Date" />
            Description:
            <Textarea bind:value={description} placeholder="Description" />

            <div>
                <div class="mb-2 font-semibold">Analysts</div>
                <div class="space-y-1">
                    {#each users as user, index}
                        <div class="flex justify-between items-center">
                            <span>{user}</span>
                            <button on:click={() => removeUser(index)} class="text-red-500 text-sm">Remove</button>
                        </div>
                    {/each}
                </div>
                <div class="flex gap-2 mt-2">
                    <Input bind:value={newUser} placeholder="Add user..." />
                    <Button on:click={addUser}>Add</Button>
                </div>

                <!-- analysts -->

            </div>
        </div>


        <DialogFooter>
            <Button on:click={() => handleSave()}>Save</Button>
            <Button variant="outline" on:click={handleCancel}>Cancel</Button>
        </DialogFooter>
    </DialogContent>
</Dialog>
