<script>
	import Sidebar_projects from '$lib/components/ui/sidebar/Sidebar_projects.svelte';
	import { ModeWatcher } from 'mode-watcher';
	import '../../../app.css';
</script>

<svelte:head>
	<title>TRACE | Project Dashboard</title>
</svelte:head>

<ModeWatcher />

<div class="bg-background flex max-h-screen">
	<div class="app-container">
		<Sidebar_projects />
	</div>
	<main class="content">
		<slot />
	</main>
</div>

<style>
	.app-container {
		display: flex;
		max-height: 100vh;
		background-color: var(--background);
	}

	.content {
		flex-grow: 1;
		overflow-y: auto;
		padding-left: 4.5rem;
	}
</style>
