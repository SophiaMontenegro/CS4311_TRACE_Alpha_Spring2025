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
	import { connectToSQLInjectionWebSocket, closeSQLInjectionWebSocket } from '$lib/services/sqlInjectionSocket';
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
	const sqlInjectionResults = derived(serviceResults, ($serviceResults) => $serviceResults.sqlinjection);
	const dynamicColumns = derived(sqlInjectionResults, ($sqlInjectionResults) =>
		$sqlInjectionResults.length > 0
			? Object.keys($sqlInjectionResults[0]).map((key) => ({
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
		[serviceStatus, sqlInjectionResults],
		([$serviceStatus, $sqlInjectionResults]) =>
			$serviceStatus.status === 'running' && $sqlInjectionResults.length > 0
	);

	const currentStep = derived(serviceStatus, ($serviceStatus) =>
		$serviceStatus.status === 'running' || $serviceStatus.status === 'paused'
			? 'running'
			: $serviceStatus.status === 'completed'
				? 'results'
				: 'config'
	);

	// Create a new store for the progress
	const fProgress = writable(0);

	// Function to simulate progress
	function simulateProgress() {
	    let progress = 0;
        const interval = setInterval(() => {
            // Check if progress already reached 100 or if service is completed
            if (progress >= 95 || $fProgress >= 100 || $serviceStatus.status === 'completed') {
                clearInterval(interval);
                return;
            }
            
            progress += Math.random() * 10;
            fProgress.set(Math.min(progress, 95));
        }, 1000);
    
        return () => clearInterval(interval);
	}

	// Create a new store for the job ID
	const fJobId = writable(null);
	
	// Function to generate a job ID
	function generateFJobId() {
	    return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
	}
	
	let resultIntervalId;
    let checkpointIntervalId;
    let completionTracked = false;

    onMount(() => {
        const jobId = localStorage.getItem('currentSQLInjectionJobId') || generateFJobId();
        fJobId.set(jobId);
        localStorage.setItem('currentSQLInjectionJobId', jobId);
        
        // Check if we're already in completed status
        if (get(serviceStatus).status === 'completed') {
            console.log('[SQLInjection] Status is already completed, trying to fetch results one more time');
            // Even if completed, try to fetch results one more time
            // IMPORTANT: Don't set completionTracked here to allow one final fetch
            fetchResults(jobId);
            return;
        }
    
        // connectToSQLInjectionWebSocket(jobId);
        const stopSimulation = simulateProgress();
        
        // Immediately try to fetch results once at startup
        fetchResults(jobId);
        
        // Store the interval ID for result fetching
        resultIntervalId = setInterval(() => {
            // Only fetch results if the scan is not completed
            const status = get(serviceStatus).status;
            if (status !== 'completed') {
                fetchResults(jobId);
            } else if (!completionTracked) {
                // If we just completed, fetch one last time then clear the interval
                fetchResults(jobId);
                completionTracked = true;
                clearAllIntervals();
            }
        }, 2000);  // Reduced from 5000 to 2000 ms for more frequent checks
        
        // Store the interval ID for checkpoint saving
        checkpointIntervalId = setInterval(() => {
            const status = get(serviceStatus).status;
            
            // Do not save checkpoints after scan is completed or idle
            if (!jobId || (status !== 'running' && status !== 'paused')) {
                return;
            }

            const data = get(serviceResults).sqlinjection;
            if (data.length > 0) {
                localStorage.setItem(`checkpoint_${jobId}`, JSON.stringify(data));
                console.log(`[Auto] Checkpoint saved for job ${jobId}`);
            }
        }, 15000);

        return () => {
            stopSimulation();
            clearAllIntervals();
            closeSQLInjectionWebSocket();
        };
    });

    // Function to clear all intervals at once
    function clearAllIntervals() {
        console.log('[SQLInjection] Clearing all intervals');
        if (resultIntervalId) clearInterval(resultIntervalId);
        if (checkpointIntervalId) clearInterval(checkpointIntervalId);
        resultIntervalId = null;
        checkpointIntervalId = null;
    }
	
	// Modify the fetchResults function
	async function fetchResults(jobId) {
        // Skip if we've already tracked completion
        if (completionTracked) {
            console.log('[SQLInjection] Skipping fetch as completion is tracked');
            return;
        }
        
        try {
            // Make the actual API call to get the results
            const res = await fetch(`http://localhost:8000/sqlmap/results/${jobId}`);
            if (!res.ok) {
                throw new Error(`Failed to fetch results: ${res.statusText}`);
            }
            
            const data = await res.json();
            
            // Check if we have a result file path
            if (data && data.result_file) {
                // Fetch the CSV content from the result file
                const csvRes = await fetch(`http://localhost:8000/sqlmap/csv/${jobId}`);
                if (!csvRes.ok) {
                    throw new Error(`Failed to fetch CSV: ${csvRes.statusText}`);
                }
                
                const csvText = await csvRes.text();
                
                // Log the received CSV text for debugging
                console.log('[SQLInjection] Received CSV:', csvText.substring(0, 200) + '...');
                
                // Parse CSV to JSON
                const parsedResults = parseCSV(csvText);
                console.log('[SQLInjection] Parsed results:', parsedResults);
                
                // Set into shared store under "sqlinjection"
                serviceResults.update((r) => ({
                    ...r,
                    sqlinjection: parsedResults
                }));
                
                // Set progress to 100% when results are received
                if ($fProgress < 100) {
                    fProgress.set(100);
                    scanProgress.set(100);
                }
                
                // Mark the scan as completed and stop all intervals
                serviceStatus.set({ status: 'completed', serviceType: 'sqlinjection', startTime: null });
                completionTracked = true;
                clearAllIntervals();
                
                console.log('[SQLInjection] Scan completed. Stopping all polling and intervals.');
            } else {
                // No results yet
                console.log('No result file available yet');
            }
        } catch (e) {
            console.error('Failed to fetch SQLInjection results:', e);
        }
    }

	// Function to parse CSV to JSON
	function parseCSV(csvText) {
	    // Split by lines and remove empty lines
	    const lines = csvText.split('\n').filter(line => line.trim() !== '');
	    if (lines.length <= 1) {
	        return [];
	    }
	    
	    // Get headers
	    const headers = lines[0].split(',').map(header => 
	        header.trim().replace(/^"|"$/g, '')
	    );
	    
	    // Parse data rows
	    const results = [];
	    for (let i = 1; i < lines.length; i++) {
	        // Handle CSV parsing correctly (respect quotes)
	        const values = parseCSVLine(lines[i]);
	        
	        if (values.length === headers.length) {
	            const row = {};
	            headers.forEach((header, index) => {
	                // Convert to camelCase for consistency
	                const key = header.toLowerCase()
	                    .replace(/\s(.)/g, (_, char) => char.toUpperCase())
	                    .replace(/\s/g, '');
	                row[key] = values[index];
	            });
	            results.push(row);
	        }
	    }
	    
	    return results;
	}

	// Helper function to parse CSV line respecting quotes
	function parseCSVLine(line) {
	    const result = [];
	    let inQuotes = false;
	    let currentValue = '';
	    
	    for (let i = 0; i < line.length; i++) {
	        const char = line[i];
	        
	        if (char === '"') {
	            // Toggle quote state
	            inQuotes = !inQuotes;
	        } else if (char === ',' && !inQuotes) {
	            // End of value
	            result.push(currentValue.trim().replace(/^"|"$/g, ''));
	            currentValue = '';
	        } else {
	            // Part of value
	            currentValue += char;
	        }
	    }
	    
	    // Add the last value
	    result.push(currentValue.trim().replace(/^"|"$/g, ''));
	    
	    return result;
	}

	// WebSocket connection
	$effect(() => {
		if ($currentStep === 'results' && $sqlInjectionResults.length === 0) {
			const jobId = localStorage.getItem('currentSQLInjectionJobId');
			if (jobId) {
				console.log('[Fetcher] Fetching results for job:', jobId);
				fetchResults(jobId);
			}
		}
	});

	const togglePause = async () => {
		if ($scanPaused) {
			await resumeScan('sqlinjection');
		} else {
			await pauseScan('sqlinjection');
		}
	};

	function handleStopCancel() {
		showStopDialog = false;
	}

	function saveCheckpoint() {
		const jobId = localStorage.getItem('currentSQLInjectionJobId');
		if (!jobId) {
			toast.error('No job ID found.');
			return;
		}

		const data = get(serviceResults).sqlinjection;
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
		closeSQLInjectionWebSocket();

		// Get the job id
		const jobId = localStorage.getItem('currentSQLInjectionJobId');
		if (!jobId) {
			console.error('No SQLInjection Job Id found in local storage');
		}

		// Clear app state
		serviceResults.update((r) => ({ ...r, sqlinjection: [] }));
		serviceStatus.set({ status: 'idle', serviceType: null, startTime: null });
		localStorage.removeItem('currentSQLInjectionJobId');

		// Tell the backend to stop
		try {
			const res = await fetch(`http://localhost:8000/api/sqlinjection/${jobId}/stop`, {
				method: 'POST'
			});
			if (res.ok) {
				console.log('SQLInjection job stopped.');
			} else {
				console.error('Failed to stop SQLInjection job:', await res.text());
			}
		} catch (e) {
			console.error('Failed to stop SQLInjection:', e);
		}

		console.log('[Stop] Service state');
		goto('/tool-dashboard');
	}

	function handleRestart() {
		stopScanProgress();

		// Reset the service results and status
		serviceResults.update((r) => ({ ...r, sqlinjection: [] }));
		serviceStatus.set({ status: 'idle', serviceType: null, startTime: null });
		localStorage.removeItem('currentSQLInjectionJobId');

		console.log('[Restart] Service state');
		goto('/SQLInjection/config');
	}

	async function handleExport() {
		// Get the current data from the store
		const results = get(sqlInjectionResults);
		if (!results || results.length === 0) {
			toast.error('No results to export.');
			return;
		}

		try {
			// Get column information from the dynamicColumns store
			const columns = get(dynamicColumns);
			
			// Use column keys and labels for the export
			const exportFields = columns.map(col => col.key);
			const headers = columns.map(col => col.label);

			// Build CSV content
			const csvRows = [
				headers.join(','), // Header row
				...results.map((row) => 
					exportFields.map((key) => {
						// Properly escape and quote values for CSV
						const value = row[key] === null || row[key] === undefined ? '' : String(row[key]);
						// Escape quotes and wrap in quotes if needed
						return `"${value.replace(/"/g, '""')}"`;
					}).join(',')
				)
			];

			// Create blob and trigger download
			const csvContent = csvRows.join('\n');
			const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
			const url = URL.createObjectURL(blob);

			const jobId = localStorage.getItem('currentSQLInjectionJobId') || 'results';
			const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
			
			const a = document.createElement('a');
			a.href = url;
			a.download = `sql_results_${jobId}.csv`;
			document.body.appendChild(a);
			a.click();
			a.remove();

			URL.revokeObjectURL(url);
			
			toast.success('Export completed!');
		} catch (error) {
			console.error('[SQLInjection Export Error]', error);
			toast.error('Failed to export results.');
		}
	}

	onDestroy(() => {
        clearAllIntervals();
        closeSQLInjectionWebSocket();
    });

</script>

<svelte:head>
	<title>SQL Injection Run | TRACE</title>
</svelte:head>

<div class="sqlinjection-run">
	<div class="title-section">
		<div class="title">
			{$currentStep === 'running' ? 'SQL Injection Scanning' : 'SQL Injection Results'}
		</div>
		<StepIndicator status={$currentStep} />
	</div>

	<div class="table">
		{#if $showProgress || $serviceStatus.status === 'completed' || $serviceStatus.status === 'paused'}
			<div class="progress-bar-container">
				<div class="progress-info">
					<div class="text-sm font-medium">Progress</div>
					<div class="text-2xl font-bold">{$fProgress.toFixed(1)}% scanned</div>
				</div>
				<Progress value={$fProgress} max={100} class="w-[100%]" />
			</div>
		{:else}
			<Spinner />
		{/if}

		{#if $sqlInjectionResults.length > 0}
			<Table data={$sqlInjectionResults} columns={$dynamicColumns} />
		{:else if $serviceStatus.status === 'completed'}
			<div class="no-results-message">
				<p>No vulnerabilities found on the target.</p>
			</div>
		{:else}
			<p>Please Wait A Moment...</p>
		{/if}
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
					title="Click to export SQL Injection results"
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
		<!-- <div class="single-button">
			<Button
				variant="secondary"
				size="default"
				class="terminal-button"
				aria-label="Open terminal"
				title="Click to open the terminal"
			>
				Terminal
			</Button>
		</div> -->
	</div>

	<Alert
		isOpen={showStopDialog}
		title="Are you absolutely sure?"
		message="This action cannot be undone. This will permanently stop the SQL Injection scan and save current progress."
		onCancel={handleStopCancel}
		onContinue={handleStopConfirm}
	/>
</div>

<style>
	.sqlinjection-run {
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
    .no-results-message {
        margin-top: 2rem;
        padding: 2rem;
        text-align: center;
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        width: 80%;
    }
    
    .no-results-message p {
        font-size: 1.25rem;
        font-weight: 500;
        color: #4b5563;
    }
</style>