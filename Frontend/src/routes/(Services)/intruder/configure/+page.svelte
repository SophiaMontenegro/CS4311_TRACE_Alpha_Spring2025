<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
    import { attackResults } from '$lib/stores/intruder';

	let requestPreview = null;
	let intrusionField = '';
	let payloads = '';
	let error = '';

	// Fetch preview data on page load
	onMount(async () => {
		try {
			const res = await fetch('http://localhost:8000/api/intruder/preview_request');
			if (!res.ok) {
				const data = await res.json();
				error = data.detail || 'Failed to load preview.';
				return;
			}
			requestPreview = await res.json();
		} catch (err) {
			error = 'Server not reachable.';
			console.error(err);
		}
	});

	async function startAttack() {
	if (!intrusionField || !payloads) {
		error = 'Please fill all fields.';
		return;
	}

	const res = await fetch('http://localhost:8000/api/intruder/run_attack', {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({
			intrusion_field: intrusionField,
			payloads: payloads.split('\n').filter(p => p.trim() !== '')
		})
	});

	const result = await res.json();
	// console.log('Attack result:', result);
    if (result.results) {
		attackResults.set(result.results);  
		goto('/intruder/scan');            
	}
}

</script>

<div class="p-6 max-w-3xl mx-auto space-y-6">
	<h1 class="text-2xl font-bold">Attack Configuration</h1>

	{#if error}
		<p class="text-red-600">{error}</p>
	{/if}

	{#if requestPreview}
		<div>
			<h2 class="font-semibold">HTTP Request Preview</h2>
			<pre class="bg-gray-100 p-4 rounded text-sm overflow-x-auto">
URL: {requestPreview.url}
Method: {requestPreview.method}
Headers: {JSON.stringify(requestPreview.headers, null, 2)}

Sample Body:
{JSON.stringify(requestPreview.sample_body, null, 2)}
			</pre>
		</div>

		<div>
			<label class="block mt-4 font-medium">Select Intrusion Field</label>
			<select bind:value={intrusionField} class="input mt-1">
				<option disabled selected value="">-- Select --</option>
				{#each Object.keys(requestPreview.sample_body) as field}
					<option value={field}>{field}</option>
				{/each}
			</select>
		</div>

		<div>
			<label class="block mt-4 font-medium">Payloads (one per line)</label>
			<textarea bind:value={payloads} class="input mt-1 w-full h-32" placeholder="admin\n123\n' OR 1=1 --"></textarea>
		</div>

		<button on:click={startAttack} class="b-start mt-4">
			Start Attack
		</button>
	{/if}
</div>

<style lang="postcss">
	@reference "tailwindcss";

	.input {
		@apply block px-4 py-2 border border-gray-300 rounded bg-white text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500;
	}

	.b-start {
		background-color: #06b6d4;
		color: white;
		padding: 0.5rem 1rem;
		border-radius: 0.25rem;
		transition: background-color 0.1s ease-in-out;
	}

	.b-start:hover {
		background-color: #4b5563;
	}
</style>
