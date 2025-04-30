<script>
	import { attackResults } from '$lib/stores/intruder';
	import { onMount } from 'svelte';
	import { getApiBaseURL } from '$lib/utils/apiBaseURL';
	let results = [];
	let projectName = "";
	let exportMessage = "";
	attackResults.subscribe(value => {
		results = value;
	});

	onMount(() => {
		projectName = localStorage.getItem('currentProjectName') || 'export';
	});

	async function exportResults() {
        try {
            const res = await fetch(`${getApiBaseURL()}/api/intruder/export_results`, {
                method: 'POST'
            });
            if (!res.ok) {
                throw new Error('Failed to export results.');
            }
            const data = await res.json();
            exportMessage = `Results exported! Job ID: ${data.job_id}`;
        } catch (err) {
            console.error(err);
            exportMessage = 'Failed to export results.';
        }
    }
</script>


<div class="p-6 max-w-4xl mx-auto">
	<h2 class="text-2xl font-bold mb-4">Attack Results</h2>

	{#if results.length === 0}
		<p>No results available. Please run an attack.</p>
	{:else}
		<table class="table-auto w-full text-sm border border-gray-300 rounded dark:bg-background3 dark:text-background3-foreground">
			<thead class="bg-gray-100 text-left">
				<tr>
					<th class="px-4 py-2 border-b dark:bg-accent">Payload</th>
					<th class="px-4 py-2 border-b dark:bg-accent">Status</th>
					<th class="px-4 py-2 border-b dark:bg-accent">Length</th>
				</tr>
			</thead>
			<tbody>
				{#each results as r}
					<tr>
						<td class="px-4 py-2 border-b">{r.payload}</td>
						<td class="px-4 py-2 border-b">{r.status_code}</td>
						<td class="px-4 py-2 border-b">{r.length}</td>
					</tr>
				{/each}
			</tbody>
		</table>
		<!-- This is the export button -->
		 <br>
		
		<!-- onclick={sendSelectedForm}  -->
		 <button  
				on:click={exportResults}
				class="bg-cyan-500 var(--foreground) px-4 py-2 rounded transition-colors duration-100 ease-in-out hover:bg-gray-400"
				>
				Export
			</button>

			{#if exportMessage}
				<p class="text-green-700 mt-2">{exportMessage}</p>
			{/if}
	{/if}
</div>
