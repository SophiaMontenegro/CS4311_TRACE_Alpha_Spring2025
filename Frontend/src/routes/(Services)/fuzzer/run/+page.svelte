<script>
	import { Button } from '$lib/components/ui/button/index.js';
	import { goto } from '$app/navigation';
	import { Progress } from '$lib/components/ui/progress/index.js';
	import { serviceStatus } from '$lib/stores/projectServiceStore.js';
	import StepIndicator from '$lib/components/ui/progressStep/ProgressStep.svelte';
	import Spinner from '$lib/components/ui/spinner/Spinner.svelte';
	import Table from '$lib/components/ui/table/Table.svelte';
	import Alert from '$lib/components/ui/alert/Alert.svelte';
	import { derived, get, writable, readable } from 'svelte/store';
	import { onMount, onDestroy } from 'svelte';
	import { toast } from 'svelte-sonner';
	import { serviceResults } from '$lib/stores/serviceResultsStore.js';
	import { connectToFuzzerWebSocket, closeFuzzerWebSocket } from '$lib/services/fuzzerSocket.js';
	import {
		scanProgress,
		scanPaused,
		startScanProgress,
		stopScanProgress,
		pauseScan,
		resumeScan
	} from '$lib/stores/scanProgressStore.js';

	const { data } = $props();
	let showStopDialog = $state(false);
	let intervalId;

	// Derived stores
	const fuzzerResults = derived(serviceResults, ($serviceResults) => $serviceResults.fuzzer);
	const dynamicColumns = derived(fuzzerResults, ($fuzzerResults) =>
		$fuzzerResults.length > 0
			? Object.keys($fuzzerResults[0]).map((key) => ({
					key,
					label: key
						.replace(/([a-z])([A-Z])/g, '$1 $2')
						.split('_')
						.map((word) => word.charAt(0).toUpperCase() + word.slice(1))
						.join(' ')
				}))
			: []
	);
	const showProgress = derived(
		[serviceStatus, fuzzerResults],
		([$serviceStatus, $fuzzerResults]) =>
			$serviceStatus.status === 'running' && $fuzzerResults.length > 0
	);

	const currentStep = derived(serviceStatus, ($serviceStatus) =>
		$serviceStatus.status === 'running' || $serviceStatus.status === 'paused'
			? 'running'
			: $serviceStatus.status === 'completed'
				? 'results'
				: 'config'
	);

	// Fetch results from the server
	async function fetchResults(jobId) {
		try {
			const res = await fetch(`http://localhost:8000/api/fuzzer/${jobId}/results`);
			const response = await res.json();
			const parsed = Array.isArray(response) ? response : (response.results ?? []);

			// Set into shared store under "fuzzer"
			serviceResults.update((r) => ({
				...r,
				fuzzer: parsed
			}));

			console.log('[Fuzzer Results]', parsed);
		} catch (e) {
			console.error('Failed to fetch fuzzer results:', e);
		}
	}

	// WebSocket connection
	$effect(() => {
		if ($currentStep === 'results' && $fuzzerResults.length === 0) {
			const jobId = localStorage.getItem('currentFuzzerJobId');
			if (jobId) {
				console.log('[Fetcher] Fetching results for job:', jobId);
				fetchResults(jobId);
			}
		}
	});

	const togglePause = async () => {
		if ($scanPaused) {
			await resumeScan('fuzzer');
		} else {
			await pauseScan('fuzzer');
		}
	};

	function handleStopCancel() {
		showStopDialog = false;
	}

	function saveCheckpoint() {
		const jobId = localStorage.getItem('currentFuzzerJobId');
		if (!jobId) {
			toast.error('No job ID found.');
			return;
		}

		const data = get(serviceResults).fuzzer;
		if (!data || data.length === 0) {
			toast.error('No results to checkpoint.');
			return;
		}

		localStorage.setItem(`checkpoint_${jobId}`, JSON.stringify(data));
		toast.success('Checkpoint saved!', {
			description: `Saved at ${new Date().toLocaleTimeString([], { hour: 'numeric', minute: '2-digit', hour12: true })}`
		});
		console.log(`[Checkpoint] Saved for job ${jobId}`);
	}

	async function handleStopConfirm() {
		showStopDialog = false;
		stopScanProgress();
		closeFuzzerWebSocket();

		// Get the job id
		const jobId = localStorage.getItem('currentFuzzerJobId');
		if (!jobId) {
			console.error('No Fuzzer Job Id found in local storage');
		}

		// Clear app state
		serviceResults.update((r) => ({ ...r, fuzzer: [] }));
		serviceStatus.set({ status: 'idle', serviceType: null, startTime: null });
		localStorage.removeItem('currentFuzzerJobId');

		// Tell the backend to stop
		try {
			const res = await fetch(`http://localhost:8000/api/fuzzer/${jobId}/stop`, {
				method: 'POST'
			});
			if (res.ok) {
				console.log('Fuzzer job stopped.');
			} else {
				console.error('Failed to stop fuzzer job:', await res.test());
			}
		} catch (e) {
			console.error('Failed to stop fuzzer:', e);
		}

		console.log('[Stop] Service state');
		goto('/dashboard');
	}

	function handleRestart() {
		stopScanProgress();

		// Reset the service results and status
		serviceResults.update((r) => ({ ...r, fuzzer: [] }));
		serviceStatus.set({ status: 'idle', serviceType: null, startTime: null });
		localStorage.removeItem('currentFuzzerJobId');

		console.log('[Restart] Service state');
		goto('/fuzzer/config');
	}

	function handleClearJob() {
		const jobId = localStorage.getItem('currentFuzzerJobId');
		if (jobId) {
			localStorage.removeItem(`checkpoint_${jobId}`);
			localStorage.removeItem('currentFuzzerJobId');
		}
		serviceResults.update((r) => ({ ...r, fuzzer: [] }));
		serviceStatus.set({ status: 'idle', serviceType: null, startTime: null });
		goto('/fuzzer/config');
		console.log('[Clear Job] Service state and local storage cleared');
	}

	async function handleExport() {
		const jobId = localStorage.getItem('currentFuzzerJobId');
		if (!jobId) {
			alert('Fuzzer job ID not found.');
			return;
		}

		try {
			const res = await fetch(`http://localhost:8000/api/fuzzer/${jobId}/results`);
			if (!res.ok) throw new Error('Failed to fetch fuzzer results.');

			const { results = [] } = await res.json();

			const exportFields = ['id', 'response', 'payload', 'length', 'error'];
			const headers = ['ID', 'Response', 'Payload', 'Length', 'Error'];

			const csvRows = [
				headers.join(','),
				...results.map((row) => exportFields.map((key) => JSON.stringify(row[key] ?? '')).join(','))
			];

			const csvContent = csvRows.join('\n');
			const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
			const url = URL.createObjectURL(blob);

			const a = document.createElement('a');
			a.href = url;
			a.download = `fuzzer_${jobId}_results.csv`;
			document.body.appendChild(a);
			a.click();
			a.remove();

			URL.revokeObjectURL(url);
		} catch (error) {
			console.error('[Fuzzer Export Error]', error);
			alert('There was an error exporting the fuzzer results.');
		}
	}

	// onMount and onDestroy lifecycle hooks
	onMount(() => {
		const jobId = localStorage.getItem('currentFuzzerJobId');
		if (jobId && get(serviceStatus).status !== 'completed') {
			connectToFuzzerWebSocket(jobId);
		}

		intervalId = setInterval(() => {
			const jobId = localStorage.getItem('currentFuzzerJobId');
			const status = get(serviceStatus);

			// Do not save checkpoints after scan is completed or idle
			if (!jobId || (status.status !== 'running' && status.status !== 'paused')) return;

			const data = get(serviceResults).fuzzer;
			if (data.length > 0) {
				localStorage.setItem(`checkpoint_${jobId}`, JSON.stringify(data));
				console.log(`[Auto] Checkpoint saved for job ${jobId}`);
			}
		}, 15000);
	});

	onDestroy(() => {
		clearInterval(intervalId);
		closeFuzzerWebSocket();
	});
</script>

<div class="fuzzer-run">
	<div class="title-section">
		<div class="title">
			{$currentStep === 'running' ? 'Fuzzer Scanning' : 'Fuzzer Results'}
		</div>
		<StepIndicator status={$currentStep} />
	</div>

	<div class="table">
		{#if $showProgress || $serviceStatus.status === 'completed' || $serviceStatus.status === 'paused'}
			<div class="progress-bar-container">
				<div class="progress-info">
					<div class="text-sm font-medium">Progress</div>
					<div class="text-2xl font-bold">{$scanProgress}% scanned</div>
				</div>
				<Progress value={$scanProgress} max={100} class="w-[100%]" />
			</div>
		{:else}
			<Spinner />
		{/if}

		<Table data={$fuzzerResults} columns={$dynamicColumns} />
	</div>

	<div class="button-section">
		<div class="left-buttons">
			{#if $serviceStatus.status === 'completed'}
				<Button
					onclick={handleRestart}
					variant="default"
					size="default"
					class="restart-button"
					aria-label="Restart the scan"
					title="Click to restart the scan"
				>
					Restart
				</Button>
				<Button
					onclick={handleExport}
					variant="secondary"
					size="default"
					class="view-all-results"
					aria-label="Export results"
					title="Click to export crawler results"
				>
					Export Results
				</Button>
			{:else if $serviceStatus.status === 'running' || $serviceStatus.status === 'paused'}
				<Button
					onclick={togglePause}
					variant="secondary"
					size="default"
					class="pause-button"
					aria-label={$scanPaused ? 'Resume the scan' : 'Pause the scan'}
					title={$scanPaused ? 'Click to resume the scan' : 'Click to pause the scan'}
				>
					{#if $scanPaused}
						Resume
					{:else}
						Pause
					{/if}
				</Button>

				<Button
					onclick={saveCheckpoint}
					variant="secondary"
					size="default"
					class="save-checkpoint"
					aria-label="Save checkpoint"
					title="Checkpoint"
				>
					Save Checkpoint
				</Button>
			{/if}
		</div>

		<div class="right-buttons">
			{#if $serviceStatus.status === 'running' || $serviceStatus.status === 'paused'}
				<Button
					onclick={() => (showStopDialog = true)}
					variant="destructive"
					size="default"
					class="stop-button"
					aria-label="Stop the scan"
					title="Click to stop the scan"
				>
					Stop
				</Button>
			{:else if $serviceStatus.status === 'error'}
				<Button
					onclick={handleClearJob}
					variant="destructive"
					size="default"
					class="clear-button"
					aria-label="Clear error state"
					title="Clear scan state and try again"
				>
					Clear Job
				</Button>
			{/if}
		</div>
	</div>

	<Alert
		isOpen={showStopDialog}
		title="Are you absolutely sure?"
		message="This action cannot be undone. This will permanently stop the fuzzer and save current progress."
		onCancel={handleStopCancel}
		onContinue={handleStopConfirm}
	/>
</div>

<svelte:head>
	<title>Fuzzer Run | TRACE</title>
</svelte:head>

<style>
	.fuzzer-run {
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

	.left-buttons,
	.right-buttons {
		display: flex;
		flex-direction: row;
		gap: 1rem;
	}
	.progress-bar-container {
		display: flex;
		flex-direction: column;
		justify-content: center;
		max-width: 100%;
		width: 80%;
		margin: 0 auto;
		padding-left: 3rem;
		padding-right: 3rem;
		padding-top: 1rem;
	}
	.progress-info {
		display: flex;
		flex-direction: column;
		justify-content: flex-start;
		width: 100%;
	}
</style>
