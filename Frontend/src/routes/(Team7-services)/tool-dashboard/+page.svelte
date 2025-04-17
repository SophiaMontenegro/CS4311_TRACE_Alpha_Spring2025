<script>
	import { goto } from '$app/navigation';
	import { Button } from '$lib/components/ui/button/index.js';
	import { serviceStatus } from '$lib/stores/projectServiceStore.js';
	import { onMount } from 'svelte';
	import { get } from 'svelte/store';

	import { connectToCrawlerWebSocket } from '$lib/services/crawlerSocket';
	import { connectToFuzzerWebSocket } from '$lib/services/fuzzerSocket';
	import { connectToBruteForceWebSocket } from '$lib/services/bruteForceSocket';

	export let data;
	$: $serviceStatus;

	onMount(() => {
		const status = get(serviceStatus).status;
		const type = get(serviceStatus).serviceType;

		if (status === 'running' || status === 'paused') {
			switch (type) {
				case 'crawler': {
					const jobId = localStorage.getItem('currentCrawlerJobId');
					if (jobId) connectToCrawlerWebSocket(jobId);
					break;
				}
				case 'fuzzer': {
					const jobId = localStorage.getItem('currentFuzzerJobId');
					if (jobId) connectToFuzzerWebSocket(jobId);
					break;
				}
				case 'dbf': {
					const jobId = localStorage.getItem('currentDbfJobId');
					if (jobId) connectToBruteForceWebSocket(jobId);
					break;
				}
			}
		}
	});

	function handleToolClick(tool) {
		const toolType = tool.name.toLowerCase();

		if (
			['running', 'paused', 'completed'].includes($serviceStatus.status) &&
			$serviceStatus.serviceType === toolType
		) {
			goto(`/${toolType}/run`);
		} else {
			goto(tool.route);
		}
	}

	function getToolStatus(tool) {
		const type = tool.name.toLowerCase();

		if ($serviceStatus.serviceType === type) {
			switch ($serviceStatus.status) {
				case 'running':
					return 'In Progress';
				case 'paused':
					return 'Paused';
				case 'completed':
					return 'Finished';
				default:
					return 'Not Started';
			}
		}
		return 'Not Started';
	}

	function getButtonLabel(tool) {
		const type = tool.name.toLowerCase();

		if ($serviceStatus.serviceType === type) {
			if ($serviceStatus.status === 'running') return 'View';
			if ($serviceStatus.status === 'paused') return 'Resume';
			if ($serviceStatus.status === 'completed') return 'View Results';
		}
		return 'Start';
	}
</script>

<div class="dashboard">
	<div class="title-section">
		<div class="title">Dashboard</div>
		<div class="proj-name">{data.projectName}</div>
	</div>

	<div class="cards-container">
		{#each data.tools as tool}
			<div class="card">
				<div class="tool-name">{tool.name}</div>
				<div class="tool-actions">
					<div class="tool-status">
						Status: {getToolStatus(tool)}
					</div>
					<Button
						default="secondary"
						size="lg"
						class={$serviceStatus.status === 'running' ? 'px-10' : ''}
						data-active={$serviceStatus.serviceType === tool.name.toLowerCase()}
						disabled={$serviceStatus.status === 'running' &&
							$serviceStatus.serviceType !== tool.name.toLowerCase()}
						onclick={() => handleToolClick(tool)}
						aria-label={getButtonLabel(tool)}
						title={getButtonLabel(tool)}
					>
						{getButtonLabel(tool)}
					</Button>
				</div>
			</div>
		{/each}
	</div>
</div>

<style>
	.dashboard {
		display: flex;
		margin-left: 4.5rem;
		height: 100vh;
		flex-direction: column;
	}

	.title-section {
		display: flex;
		flex-direction: column;
		max-height: fit-content;
		padding-bottom: 2rem;
	}

	.title {
		font-size: 2rem;
		font-style: normal;
		font-weight: 600;
		padding-left: 3rem;
		padding-top: 3rem;
	}

	.proj-name {
		font-size: 1.2rem;
		font-style: normal;
		font-weight: 600;
		padding-left: 3rem;
		padding-top: 0.5rem;
		color: var(--foreground);
	}

	.cards-container {
		display: flex;
		flex-direction: column;
		align-items: flex-start;
		padding-left: 3rem;
		padding-right: 3rem;
		max-width: 100%;
		gap: 2rem;
	}

	.card {
		border-radius: 0.6rem;
		width: 100%;
		background-color: var(--background1);
		display: flex;
		flex-direction: row;
		align-items: center;
		justify-content: space-between;
		padding: 1rem 2.5rem 1rem 2.5rem;
	}

	.tool-name {
		font-size: 1.1rem;
		font-style: normal;
		font-weight: 500;
	}

	.tool-actions {
		display: flex;
		align-items: center;
		gap: 2rem;
	}

	.tool-status {
		font-size: 1rem;
		font-style: normal;
		font-weight: 400;
		color: var(--foreground);
	}
</style>
