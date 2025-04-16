<script>
	import { Button } from '$lib/components/ui/button/index.js';
	import { goto } from '$app/navigation';
	import { Progress } from '$lib/components/ui/progress/index.js';
	import { onMount, onDestroy } from 'svelte';
	import StepIndicator from '$lib/components/ui/progressStep/ProgressStep.svelte';
	import Table from '$lib/components/ui/table/Table.svelte';
	import Spinner from '$lib/components/ui/spinner/Spinner.svelte';
	import { serviceResults } from '$lib/stores/serviceResultsStore.js';
	import { serviceStatus } from '$lib/stores/projectServiceStore.js';
	import {
		connectToCredGenAIWebSocket,
		closeCredGenAIWebSocket
	} from '$lib/services/credGenAISocket.js';
	import { derived, get, writable, readable } from 'svelte/store';

	const { data } = $props();
	let value = $state(15);

	const exporting = writable(false);

	const credGenAIResults = derived(serviceResults, ($serviceResults) => {
		const results = $serviceResults.credGenAI ?? [];
		return results;
	});

	const dynamicColumns = derived(credGenAIResults, ($credGenAIResults) => {
		const excludedKeys = ['password_evaluation'];

		const columns =
			$credGenAIResults.length > 0
				? Object.keys($credGenAIResults[0])
						.filter((key) => !excludedKeys.includes(key))
						.map((key) => ({
							key,
							label: key
								.replace(/([a-z])([A-Z])/g, '$1 $2')
								.split('_')
								.map((word) => word.charAt(0).toUpperCase() + word.slice(1))
								.join(' ')
						}))
				: [];
		console.log('[Derived Store] dynamicColumns:', columns);
		return columns;
	});

	const currentStep = derived(serviceStatus, ($serviceStatus) =>
		$serviceStatus.status === 'running' || $serviceStatus.status === 'paused'
			? 'running'
			: $serviceStatus.status === 'completed'
				? 'results'
				: 'config'
	);

	async function fetchResults(jobId) {
		try {
			const res = await fetch(`http://localhost:8000/api/ml/${jobId}/results`);
			const response = await res.json();
			const parsed = Array.isArray(response) ? response : (response.results ?? []);

			// Set into shared store under "credGenAI"
			serviceResults.update((r) => ({
				...r,
				credGenAI: parsed
			}));

			console.log('[CredGenAI Results]', parsed);
		} catch (e) {
			console.error('Failed to fetch credGenAI results:', e);
		}
	}

	$effect(() => {
		if ($currentStep === 'results' && $credGenAIResults.length === 0) {
			const jobId = localStorage.getItem('currentCredGenAIJobId');
			if (jobId) {
				console.log('[Fetcher] Fetching results for job:', jobId);
				fetchResults(jobId);
			}
		}
	});

	function handleRestart() {
		closeCredGenAIWebSocket();

		// Get the job id
		const jobId = localStorage.getItem('currentCredGenAIJobId');
		if (!jobId) {
			console.error('No CredGenAI Job Id found in local storage');
		}
		// Reset the service results and status
		serviceResults.update((r) => ({ ...r, credGenAI: [] }));
		serviceStatus.set({ status: 'idle', serviceType: null, startTime: null });
		localStorage.removeItem('currentCredGenAIJobId');

		console.log('[Restart] Service state');
		goto('/credGenAI/config');
	}

	async function handleExportWordList() {
		try {
			const jobId = localStorage.getItem('currentCredGenAIJobId');
			if (!jobId) throw new Error('Job ID not found');

			const res = await fetch(`http://localhost:8000/api/ml/${jobId}/results`);
			if (!res.ok) throw new Error('Failed to fetch results');

			const json = await res.json();
			const results = json.results ?? [];

			// Define the exact fields you want to include
			const fields = ['id', 'username', 'username_score', 'password', 'is_secure'];

			// Convert to CSV
			const csvRows = [
				fields.join(','),
				...results.map((entry) => fields.map((key) => JSON.stringify(entry[key] ?? '')).join(','))
			];

			const csvContent = csvRows.join('\n');
			const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
			const url = window.URL.createObjectURL(blob);

			// Trigger download
			const a = document.createElement('a');
			a.href = url;
			a.download = `credGenAI_${jobId}_results.csv`;
			document.body.appendChild(a);
			a.click();
			a.remove();
			window.URL.revokeObjectURL(url);
		} catch (err) {
			alert('Failed to export results');
			console.error('[CredGenAI Export Error]', err);
		}
	}

	onMount(() => {
		let jobId = localStorage.getItem('currentCredGenAIJobId');
		if (!jobId && data?.jobId) {
			jobId = data.jobId;
			localStorage.setItem('currentCredGenAIJobId', jobId);
		}

		if (jobId) {
			console.log('[Reconnect] Connecting to WebSocket with job ID:', jobId);

			serviceStatus.set({
				status: 'running',
				serviceType: 'credGenAI',
				startTime: new Date().toISOString()
			});

			connectToCredGenAIWebSocket(jobId);
		} else {
			console.warn('[Reconnect] No credGenAI job ID found in localStorage.');
		}
	});

	onDestroy(() => {
		closeCredGenAIWebSocket();
	});
</script>

<svelte:head>
	<title>CredGenAI Run | TRACE</title>
</svelte:head>

<div class="generator-run">
	<div class="title-section">
		<div class="title">
			{$currentStep === 'running' ? 'Generating Credentials' : 'Credential Results'}
		</div>
		<StepIndicator status={$currentStep} />
	</div>

	<div class="table">
		{#if $currentStep === 'running'}
			<Spinner style="margin-bottom: 1rem;" />
			<div class="text-primary" style="font-size: 1rem; font-weight: bold; margin-top: 1rem;">
				Generating credentials...
			</div>
		{:else if $credGenAIResults.length > 0}
			<Table data={$credGenAIResults} columns={$dynamicColumns} />
		{/if}
	</div>

	{#if $currentStep !== 'running'}
		<div class="button-section">
			<div class="button-left">
				<Button
					onclick={handleRestart}
					variant="secondary"
					size="default"
					class="restart-button"
					aria-label="Re-generate the configuration"
					title="Re-generate the configuration"
				>
					Re-Generate
				</Button>
			</div>

			<!-- Right button -->
			<div class="button-right">
				<Button
					onclick={handleExportWordList}
					variant="default"
					size="default"
					class="save-button"
					aria-label="Save the word list"
					title="Save the word list"
				>
					Export Results
				</Button>
			</div>
		</div>
	{/if}
</div>

<style>
	.generator-run {
		display: flex;
		margin-left: 4.5rem;
		height: 100vh;
		flex-direction: column;
	}
	.title-section {
		display: flex;
		flex-direction: row;
		justify-content: space-between;
		width: 100%;
		max-height: fit-content;
		padding-right: 3rem;
	}
	.title {
		font-size: 2rem;
		font-style: normal;
		font-weight: 600;
		padding-left: 3rem;
		padding-top: 3rem;
	}
	.table {
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		height: 100%;
	}
	.button-section {
		display: flex;
		justify-content: space-between;
		align-items: center;
		width: 100%;
		padding: 0rem 8rem 3rem 8rem;
	}

	.button-left,
	.button-right {
		display: flex;
	}
</style>
