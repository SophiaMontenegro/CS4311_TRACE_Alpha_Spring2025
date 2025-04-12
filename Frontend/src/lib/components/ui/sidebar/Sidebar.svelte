<script>
	import { beforeUpdate, onMount } from 'svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Hammer, Network, FileCheck, Brain, Settings } from 'lucide-svelte';
	import { toggleMode, mode } from 'mode-watcher';
	import { goto } from '$app/navigation';

	let selectedIndex;

	function isSelected(index, route) {
		selectedIndex = index;
		localStorage.setItem('selectedIndex', index);
		goto(route || '/dashboard');
	}

	const menuItems = [
		{ icon: Hammer, tooltip: 'Tools', route: '/dashboard' },
		{ icon: Network, tooltip: 'Network' },
		{ icon: FileCheck, tooltip: 'Results' },
		{ icon: Brain, tooltip: 'AI Model', route: '/credGenAI/config' },
	];

	onMount(() => {
		const savedIndex = localStorage.getItem('selectedIndex');
		if (savedIndex !== null) {
			selectedIndex = parseInt(savedIndex, 10);
		}
	});

	beforeUpdate(() => {
		if (selectedIndex === undefined) {
			const savedIndex = localStorage.getItem('selectedIndex');
			if (savedIndex !== null) {
				selectedIndex = parseInt(savedIndex, 10);
			} else {
				selectedIndex = 0;
			}
		}
	});
</script>

<div class="sidebar">
	<div class="home-button">
		<Button
			onclick={() => isSelected(0, '/dashboard')}
			variant="ghost"
			size="icon"
			type="button"
			title="TRACE Home"
			aria-label="TRACE Home"
		>
			{#if $mode === 'dark'}
				<img
					src="/icons/traceDarkIcon.svg"
					alt="Dark Mode Icon"
					style="width: 2.5rem; height: 2.5;"
				/>
			{:else}
				<img
					src="/icons/traceLightIcon.svg"
					alt="Light Mode Icon"
					style="width: 2.5rem; height: 2.5;"
				/>
			{/if}
		</Button>
	</div>
	<div class="main-buttons">
		{#each menuItems as item, index}
			<Button
				variant="circle"
				size="circle"
				type="button"
				onclick={() => isSelected(index, item.route)}
				data-active={selectedIndex === index}
				title={item.tooltip}
			>
				<item.icon style="width: 20px; height: 20px;" />
			</Button>
		{/each}
	</div>
	<div class="settings-button">
		<Button onclick={toggleMode} variant="circle" size="circle" type="button" title="Settings">
			<Settings style="width: 20px; height: 20px;" />
		</Button>
	</div>
</div>

<style>
	.sidebar {
		position: fixed;
		left: 0;
		top: 0;
		height: 100vh;
		max-width: 4.5rem;
		background-color: var(--background1);
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: 2rem 1.3rem;
		border-radius: 0 0.9375rem 0.9375rem 0;
		box-shadow: 0px 3px 12px 0px rgba(0, 0, 0, 0.25);
	}

	.home-button {
		display: flex;
		justify-content: center;
		align-items: center;
		height: 1.5rem;
	}

	.main-buttons {
		display: flex;
		flex-direction: column;
		gap: 1rem;
		flex-grow: 1;
		justify-content: center;
	}

	.settings-button {
		display: flex;
		justify-content: center;
		align-items: center;
		height: 1.5rem;
	}
</style>
