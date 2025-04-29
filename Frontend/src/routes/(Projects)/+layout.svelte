<script>
	import Sidebar_projects from '$lib/components/ui/sidebar/Sidebar_projects.svelte';
	import { ModeWatcher } from 'mode-watcher';
	import '../../app.css';
</script>

<svelte:head>
	<title>TRACE | Project Dashboard</title>
</svelte:head>

<ModeWatcher />

<div class="bg-background flex h-screen overflow-hidden">
	<main class="flex-1 overflow-hidden p-4">
		<slot />
	</main>
</div>
