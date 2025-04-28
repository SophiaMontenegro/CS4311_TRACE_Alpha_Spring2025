<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { attackResults, targetUrlStore, modeStore} from '$lib/stores/intruder'; 

	export let formIndex = 0;
	export let noForm = false;
	let detectedMode = '';
	let targetUrlValue = '';
	let requestPreview = null;
	let intrusionField = '';
	let payloads = '';
	let error = '';
	let attackType = 'html_form';
	let apiEndpoint = '';
	let paramName = '';
	let baseBody = '{}'; // JSON as string

	targetUrlStore.subscribe(value => {
		targetUrlValue = value;
	});
	modeStore.subscribe(value => {
    detectedMode = value;
		});

	onMount(async () => {
		try {
			if (!noForm) {
				const res = await fetch('http://localhost:8000/api/intruder/preview_request');
				if (!res.ok) {
					const data = await res.json();
					error = data.detail || 'Failed to load preview.';
					return;
				}
				requestPreview = await res.json();
				if (detectedMode == 'json'){
					attackType = 'api'; 
					apiEndpoint = targetUrlValue;
				}
				else{
					attackType = 'urlencoded'; 
					apiEndpoint = targetUrlValue;
				}
			} else {
				attackType = 'html_form'; 
			}
		} catch (err) {
			error = 'Server not reachable.';
			console.error(err);
		}
	});

	async function startAttack() {
		try {
			if (!intrusionField || !payloads) {
				error = 'Please fill all required fields.';
				return;
			}

			const payloadList = payloads.split('\n').filter(p => p.trim() !== '');
			if (payloadList.length === 0) {
				error = 'Please provide at least one payload.';
				return;
			}

			const body = {
				intrusion_field: intrusionField,
				payloads: payloadList,
				attack_type: attackType
			};

			if (attackType === 'api') {
				if (!apiEndpoint || !baseBody || !isValidUrl(apiEndpoint) || !isValidJson(baseBody)) {
					error = 'API attack requires a valid URL and a valid JSON body.';
					return;
				}
				body.api_endpoint = apiEndpoint;
				body.base_body = JSON.parse(baseBody);
			}

			if (attackType === 'urlencoded') {
				if (!apiEndpoint || !paramName || !isValidUrl(apiEndpoint)) {
					error = 'URL-encoded attack requires a valid URL and parameter name.';
					return;
				}
				body.api_endpoint = apiEndpoint;
				body.param_name = paramName;
			}

			const res = await fetch('http://localhost:8000/api/intruder/run_attack', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(body)
			});

			if (!res.ok) {
				throw new Error(`HTTP error! status: ${res.status}`);
			}

			const result = await res.json();
			if (result.results) {
				attackResults.set(result.results);
				goto('/intruder/scan'); // ✅ After attack, go back to scan
			} else {
				error = 'Attack failed: No results returned.';
			}
		} catch (err) {
			error = `Attack failed: ${err.message}`;
			console.error('Attack error:', err);
		}
	}

	// ✅ Validation helpers
	function isValidUrl(url) {
		try {
			new URL(url);
			return true;
		} catch (_) {
			return false;
		}
	}

	function isValidJson(str) {
		try {
			JSON.parse(str);
			return true;
		} catch (_) {
			return false;
		}
	}
</script>


<!-- UI layout stays the same as yours -->

<div class="p-6 max-w-3xl mx-auto space-y-6">
	<h1 class="text-2xl font-bold">Attack Configuration</h1>

	{#if error}
		<p class="text-red-600">{error}</p>
	{/if}

	<!-- Attack Type Selection -->
	<div>
		<label class="block mt-4 font-medium">Attack Type</label>
		<select bind:value={attackType} class="input mt-1">
			<option value="html_form" disabled={!noForm}>HTML Form Attack</option>
			<option value="api" disabled={noForm}>API (JSON) Attack</option>
			<option value="urlencoded" disabled={noForm}>URL-Encoded Attack</option>
		</select>
		
	</div>

	<!-- Form Preview (only if available) -->
	{#if !noForm && requestPreview && requestPreview.sample_body}
		<div class="mt-4">
			<h2 class="font-semibold">HTTP Request Preview</h2>
			<pre class="bg-gray-100 p-4 rounded text-sm overflow-x-auto">
URL: {requestPreview?.url || 'N/A'}
Method: {requestPreview?.method || 'N/A'}
Headers: {JSON.stringify(requestPreview?.headers || {}, null, 2)}

Sample Body:
{JSON.stringify(requestPreview?.sample_body || {}, null, 2)}
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
	{/if}

	<!-- Manual Input if no form or special attack -->
	{#if noForm || attackType !== 'html_form'}
		<div>
			<label class="block mt-4 font-medium">Intrusion Field (Param / JSON Key)</label>
			<input type="text" bind:value={intrusionField} class="input mt-1" placeholder="e.g., username or search" />
		</div>
	{/if}

	<!-- API Attack Fields -->
	{#if attackType === 'api'}
		<div>
			<label class="block mt-4 font-medium">API Endpoint URL</label>
			<input type="text" bind:value={apiEndpoint} class="input mt-1" placeholder="https://example.com/api/login" />
		</div>

		<div>
			<label class="block mt-4 font-medium">Base JSON Body</label>
			<textarea bind:value={baseBody} class="input mt-1 w-full h-32"></textarea>
		</div>
	{/if}

	<!-- URL-encoded Attack Fields -->
	{#if attackType === 'urlencoded'}
		<div>
			<label class="block mt-4 font-medium">Endpoint URL</label>
			<input type="text" bind:value={apiEndpoint} class="input mt-1" placeholder="https://example.com/search" />
		</div>

		<div>
			<label class="block mt-4 font-medium">Parameter Name</label>
			<input type="text" bind:value={paramName} class="input mt-1" placeholder="e.g., q or search" />
		</div>
	{/if}

	<!-- Payloads Section -->
	<div>
		<label class="block mt-4 font-medium">Payloads (one per line)</label>
		<textarea bind:value={payloads} class="input mt-1 w-full h-32" placeholder="admin\n123\n' OR 1=1 --"></textarea>
	</div>

	<!-- Start Attack -->
	<button on:click={startAttack} class="b-start mt-4">
		Start Attack
	</button>
</div>

<style lang="postcss">
	@reference "tailwindcss";

	.input {
		@apply block w-full px-4 py-2 border border-gray-300 rounded bg-white text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500;
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
