<script>
	import { attackResults } from '$lib/stores/intruder';

	let results = [];

	attackResults.subscribe(value => {
		results = value;
	});
</script>

<div class="p-6 max-w-4xl mx-auto">
	<h2 class="text-2xl font-bold mb-4">Attack Results</h2>

	{#if results.length === 0}
		<p>No results available. Please run an attack.</p>
	{:else}
		<table class="table-auto w-full text-sm border border-gray-300 rounded">
			<thead class="bg-gray-100 text-left">
				<tr>
					<th class="px-4 py-2 border-b">Payload</th>
					<th class="px-4 py-2 border-b">Status</th>
					<th class="px-4 py-2 border-b">Length</th>
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
	{/if}
</div>
