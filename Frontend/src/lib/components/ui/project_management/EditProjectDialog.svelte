<script>
    import { Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '$lib/components/ui/dialog/index.js';
    import { Button } from '$lib/components/ui/button/index.js';
    import { Input } from '$lib/components/ui/input/index.js';
    import { Textarea } from '$lib/components/ui/textarea/index.js';

    export let project;
    export let onSave = () => {};
    let name = project.name;
    let endDate = project.endDate || '';
    let description = project.description || '';
    let users = [...(project.users || [])];
    let newUser = '';

    function addUser() {
        if (newUser.trim()) {
            users = [...users, newUser.trim()];
            newUser = '';
        }
    }

    function removeUser(index) {
        users.splice(index, 1);
    }

    function save() {
        onSave({
            ...project,
            name,
            endDate,
            description,
            users,
        });
    }
</script>

<Dialog>
    <DialogTrigger let:open>
        <button on:click={open} class="w-full text-left">Edit</button>
    </DialogTrigger>
    <DialogContent class="max-w-lg">
        <DialogHeader>
            <DialogTitle>Edit Project</DialogTitle>
        </DialogHeader>

        <div class="space-y-4">
            <Input bind:value={name} placeholder="Project Name" />
            <Input bind:value={endDate} type="date" placeholder="End Date" />
            <Textarea bind:value={description} placeholder="Description" />

            <div>
                <div class="mb-2 font-semibold">Users</div>
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
            </div>
        </div>

        <DialogFooter>
            <Button on:click={save}>Save</Button>
        </DialogFooter>
    </DialogContent>
</Dialog>
