<script>
	import { goto } from '$app/navigation';
	import { Button } from '$lib/components/ui/button/index.js';
	import { serviceStatus } from '$lib/stores/projectServiceStore.js';
	import { onMount } from 'svelte';
	import { get } from 'svelte/store';

	import { connectToCrawlerWebSocket } from '$lib/services/crawlerSocket';
	import { connectToFuzzerWebSocket } from '$lib/services/fuzzerSocket';
	import { connectToBruteForceWebSocket } from '$lib/services/bruteForceSocket';
	import { scanProgress } from '$lib/stores/scanProgressStore.js';
	import { Check, X, Circle } from 'lucide-svelte';

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

	function getServiceType(tool) {
		const name = tool.name.toLowerCase();
		if (name.includes('brute')) return 'dbf';
		if (name.includes('crawler')) return 'crawler';
		if (name.includes('fuzzer')) return 'fuzzer';
		return null;
	}

	function getToolRouteSegment(serviceType) {
		switch (serviceType) {
			case 'dbf':
				return 'bruteForce';
			case 'crawler':
				return 'crawler';
			case 'fuzzer':
				return 'fuzzer';
			default:
				return serviceType;
		}
	}

	function handleToolClick(tool) {
		const type = getServiceType(tool);
		const routeSegment = getToolRouteSegment(type);

		// If service is idle and the user is starting a new scan
		if ($serviceStatus.status === 'idle' && $serviceStatus.serviceType !== type) {
			// Reset the serviceStatus when clicking "Start"
			serviceStatus.set({
				status: 'idle',
				serviceType: null,
				startTime: null
			});
		}

		if (
			['running', 'paused', 'completed', 'error'].includes($serviceStatus.status) &&
			$serviceStatus.serviceType === type
		) {
			goto(`/${routeSegment}/run`);
		} else {
			goto(tool.route);
		}
	}

	function getToolStatus(tool) {
		const type = getServiceType(tool);

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
		const type = getServiceType(tool);

		if ($serviceStatus.serviceType === type) {
			if ($serviceStatus.status === 'running') return 'View';
			if ($serviceStatus.status === 'paused') return 'Resume';
			if ($serviceStatus.status === 'completed') return 'View Results';
		}
		return 'Start';
	}

	function getToolProgressDisplay(tool) {
		const type = getServiceType(tool);
		if ($serviceStatus.serviceType === type) {
			switch ($serviceStatus.status) {
				case 'running':
					return {
						rawStatus: 'running',
						percent: `${$scanProgress}%`,
						statusText: 'Scanning...'
					};
				case 'paused':
					return {
						rawStatus: 'paused',
						percent: `${$scanProgress}%`,
						statusText: 'Paused'
					};
				case 'completed':
					return {
						rawStatus: 'completed',
						percent: '100%',
						statusText: 'Completed'
					};
				case 'error':
					return {
						rawStatus: 'error',
						percent: `${$scanProgress}%`,
						statusText: 'ERROR!'
					};
			}
		}
		return {
			rawStatus: 'idle',
			percent: '0%',
			statusText: 'Ready to Go!'
		};
	}
</script>

<div class="dashboard">
	<div class="title-section">
		<div class="title">Dashboard</div>
		<div class="proj-name">{data.projectName}</div>
	</div>

	<div class="cards-container">
		{#each data.tools as tool (tool.name)}
			{@const display = getToolProgressDisplay(tool)}

			<div class="card">
				<div class="tool-name">{tool.name}</div>

				<div class="tool-actions">
					<div class="status-group">
						<div class="status-icon {display.rawStatus}">
							{#if display.rawStatus === 'completed'}
								<span class="icon"><Check /></span>
							{:else if display.rawStatus === 'error'}
								<span class="icon"><X /></span>
							{:else}
								<div class="center-dot"></div>
							{/if}
						</div>
					</div>
					<span>
						<span class="percent">{display.percent}</span>
						<span class="status-text"> {display.statusText}</span>
					</span>
				</div>

				<div class="buttons-container">
					<Button
						default="secondary"
						size="lg"
						class={$serviceStatus.status === 'running' ? 'px-10' : ''}
						data-active={$serviceStatus.serviceType === tool.name.toLowerCase()}
						disabled={$serviceStatus.status === 'running' &&
							$serviceStatus.serviceType !== getServiceType(tool)}
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
		font-weight: 600;
		width: 70%;
	}

	.percent {
		font-size: 1.1rem;
		font-weight: 700;
		color: var(--foreground);
	}

	.status-text {
		font-size: 0.9rem;
		font-weight: 500;
		color: var(--foreground);
		opacity: 0.85;
	}

	.tool-actions {
		display: flex;
		align-items: center;
		gap: 1rem;
		width: 16%;
	}

	.buttons-container {
		display: flex;
		align-items: center;
		justify-content: flex-end;
		width: 14%;
	}

	.status-icon {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 40px;
		height: 40px;
		border-radius: 9999px;
		font-size: 1.25rem;
		font-weight: bold;
	}

	.status-icon.completed {
		background-color: var(--success);
		color: var(--success-foreground);
	}

	.status-icon.error {
		background-color: var(--error);
		color: var(--success-foreground);
	}

	.status-icon.running {
		border: 2px solid var(--accent);
		background-color: transparent;
		color: var(--accent);
	}

	.status-icon.idle {
		border: 2px solid var(--background3);
		background-color: transparent;
		color: var(--background3);
	}

	.status-icon.paused {
		border: 2px solid var(--warning);
		background-color: transparent;
		color: var(--warning);
	}

	.center-dot {
		width: 10px;
		height: 10px;
		border-radius: 9999px;
		background-color: currentColor;
	}
</style>
