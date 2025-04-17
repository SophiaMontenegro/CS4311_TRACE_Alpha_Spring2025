<script>
	import { Button } from '$lib/components/ui/button/index.js';
	import { goto } from '$app/navigation';
	import { Progress } from '$lib/components/ui/progress/index.js';
	import { onMount, onDestroy } from 'svelte';
	import { serviceStatus } from '$lib/stores/projectServiceStore.js';
	import StepIndicator from '$lib/components/ui/progressStep/ProgressStep.svelte';
	import Spinner from '$lib/components/ui/spinner/Spinner.svelte';
	import Table from '$lib/components/ui/table/Table.svelte';
	import Alert from '$lib/components/ui/alert/Alert.svelte';
	import { derived, get, writable } from 'svelte/store';
	import { serviceResults } from '$lib/stores/serviceResultsStore.js';
	import { toast } from 'svelte-sonner';
	import { connectToBruteForceWebSocket, closeBruteForceWebSocket } from '$lib/services/bruteForceSocket.js';
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
	const bruteForceResults = derived(serviceResults, ($serviceResults) => $serviceResults.bruteForce);
	const dynamicColumns = derived(bruteForceResults, ($bruteForceResults) =>
		$bruteForceResults.length > 0
			? Object.keys($bruteForceResults[0]).map((key) => ({
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
		[serviceStatus, bruteForceResults],
		([$serviceStatus, $bruteForceResults]) =>
			$serviceStatus.status === 'running' && $bruteForceResults.length > 0
	);

	const currentStep = derived(serviceStatus, ($serviceStatus) =>
		$serviceStatus.status === 'running' || $serviceStatus.status === 'paused'
			? 'running'
			: $serviceStatus.status === 'complete'
				? 'results'
				: 'config'
	);

	// Fetch results from the server
	async function fetchResults(jobId) {
		try {
			const res = await fetch(`http://localhost:8000/api/dbf/${jobId}/results`);
			const response = await res.json();
			const parsed = Array.isArray(response) ? response : (response.results ?? []);

			// Set into shared store under "bruteForce"
			serviceResults.update((r) => ({
				...r,
				bruteForce: parsed
			}));

		} catch (e) {
			console.error('Failed to fetch bruteForce results:', e);
		}
	}

	// WebSocket connection
	$effect(() => {
		if ($currentStep === 'results' && $bruteForceResults.length === 0) {
			const jobId = localStorage.getItem('currentBruteForceJobId');
			if (jobId) {
				console.log('[Fetcher] Fetching results for job:', jobId);
				fetchResults(jobId);
			}
		}
	});

	const togglePause = async () => {
		if ($scanPaused) {
			await resumeScan('bruteForce');
		} else {
			await pauseScan('bruteForce');
		}
	};

	function handleStopCancel() {
		showStopDialog = false;
	}

	function saveCheckpoint() {
		const jobId = localStorage.getItem('currentBruteForceJobId');
		if (!jobId) {
			toast.error('No job ID found.');
			return;
		}

		const data = get(serviceResults).bruteForce;
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
		closeBruteForceWebSocket();

		// Get the job id
		const jobId = localStorage.getItem('currentBruteForceJobId');
		if (!jobId) {
			console.error('No BruteForce Job Id found in local storage');
		}

		// Clear app state
		serviceResults.update((r) => ({ ...r, bruteForce: [] }));
		serviceStatus.set({ status: 'idle', serviceType: null, startTime: null });
		localStorage.removeItem('currentBruteForceJobId');

		// Tell the backend to stop
		try {
			const res = await fetch(`http://localhost:8000/api/dbf/${jobId}/stop`, {
				method: 'POST'
			});
			if (res.ok) {
				console.log('BruteForce job stopped.');
			} else {
				console.error('Failed to stop bruteForce job:', await res.test());
			}
		} catch (e) {
			console.error('Failed to stop bruteForce:', e);
		}

		console.log('[Stop] Service state');
		goto('/dashboard');
	}

	function handleRestart() {
		stopScanProgress();

		// Reset the service results and status
		serviceResults.update((r) => ({ ...r, bruteForce: [] }));
		serviceStatus.set({ status: 'idle', serviceType: null, startTime: null });
		localStorage.removeItem('currentBruteForceJobId');

		console.log('[Restart] Service state');
		goto('/bruteForce/config');
	}

	async function handleExport() {
		const jobId = localStorage.getItem('currentBruteForceJobId');
		if (!jobId) {
			console.log('BruteForce job ID not found.');
			return;
		}

		try {
			const res = await fetch(`http://localhost:8000/api/dbf/${jobId}/results`);
			if (!res.ok) throw new Error('Failed to fetch bruteForce results.');

			const { results = [] } = await res.json();

			// Fields you want to include in the export
			const exportFields = [
				'url',
				'parentUrl',
				'title',
				'wordCount',
				'charCount',
				'linksFound',
				'error'
			];

			// Optional: Human-readable column names
			const headers = [
				'URL',
				'Parent URL',
				'Title',
				'Word Count',
				'Character Count',
				'Links Found',
				'Error'
			];

			// Build CSV content
			const csvRows = [
				headers.join(','), // Header row
				...results.map((row) => exportFields.map((key) => JSON.stringify(row[key] ?? '')).join(','))
			];

			// Create blob and trigger download
			const csvContent = csvRows.join('\n');
			const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
			const url = URL.createObjectURL(blob);

			const a = document.createElement('a');
			a.href = url;
			a.download = `bruteForce_${jobId}_results.csv`;
			document.body.appendChild(a);
			a.click();
			a.remove();

			URL.revokeObjectURL(url);
		} catch (error) {
			console.error('[BruteForce Export Error]', error);
		}
	}

	// Restore checkpoint on mount
	onMount(() => {
		const jobId = localStorage.getItem('currentBruteForceJobId');

		// Restore checkpoint if available
		if (jobId) {
			const savedCheckpoint = localStorage.getItem(`checkpoint_${jobId}`);
			if (savedCheckpoint) {
				try {
					const parsed = JSON.parse(savedCheckpoint);
					if (Array.isArray(parsed) && parsed.length > 0) {
						serviceResults.update((r) => ({ ...r, bruteForce: parsed }));
						console.log('[Restore] Checkpoint loaded for job', jobId);
					}
				} catch (err) {
					console.error('[Restore] Failed to parse checkpoint data:', err);
				}
			}
			connectToBruteForceWebSocket(jobId);
		} else {
			console.warn('No bruteForce job ID found in localStorage.');
		}

		intervalId = setInterval(() => {
			const jobId = localStorage.getItem('currentBruteForceJobId');
			const status = get(serviceStatus);

			// Do not save checkpoints after scan is complete or idle
			if (!jobId || (status.status !== 'running' && status.status !== 'paused')) return;

			const data = get(serviceResults).bruteForce;
			if (data.length > 0) {
				localStorage.setItem(`checkpoint_${jobId}`, JSON.stringify(data));
				console.log(`[Auto] Checkpoint saved for job ${jobId}`);
			}
		}, 15000);
	});

	onDestroy(() => {
		clearInterval(intervalId);
		closeBruteForceWebSocket();
	});
</script>

<svelte:head>
	<title>Brute Force Run | TRACE</title>
</svelte:head>

<div class="bruteForce-run">
	<div class="title-section">
		<div class="title">
			{$currentStep === 'running' ? 'Brute Force Scanning' : 'Brute Force Results'}
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

		<Table data={$bruteForceResults} columns={$dynamicColumns} />
	</div>

	<div class="button-section">
		<div class="button-group">
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
					title="Click to save checkpoint"
				>
					Save Checkpoint
				</Button>

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
			{/if}
		</div>
		<div class="single-button">
			<Button
				variant="secondary"
				size="default"
				class="terminal-button"
				aria-label="Open terminal"
				title="Click to open the terminal"
			>
				Terminal
			</Button>
		</div>
	</div>

	<Alert
		isOpen={showStopDialog}
		title="Are you absolutely sure?"
		message="This action cannot be undone. This will permanently stop the brute force and save current progress."
		onCancel={handleStopCancel}
		onContinue={handleStopConfirm}
	/>
</div>

<style>
	.bruteForce-run {
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
		flex-direction: row;
		justify-content: space-between;
		width: 100%;
		padding: 0rem 8rem 3rem 8rem;
	}
	.button-group {
		display: flex;
		flex-direction: row;
		gap: 1rem;
	}
	.single-button {
		display: flex;
		flex-direction: row;
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
