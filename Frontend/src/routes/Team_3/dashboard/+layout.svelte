<script>
    import Sidebar_projects from "$lib/components/ui/sidebar/Sidebar_projects.svelte";
    import { ModeWatcher } from "mode-watcher";
    import "../../../app.css";
</script>
<svelte:head>
    <title>TRACE | Project Dashboard</title>
</svelte:head>

<ModeWatcher />

<div class="flex max-h-screen bg-background">
    <div class="w-64 shrink-0">
        <Sidebar_projects />
    </div>
    <main class="flex-1 overflow-y-auto p-4">
        <slot />
    </main>
</div>
