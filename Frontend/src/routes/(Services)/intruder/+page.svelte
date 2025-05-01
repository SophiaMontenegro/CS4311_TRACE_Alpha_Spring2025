<script>
	import { goto } from "$app/navigation";
	import { targetUrlStore, modeStore } from '$lib/stores/intruder';
	import {Button} from '$lib/components/ui/button';
	import { getApiBaseURL } from '$lib/utils/apiBaseURL';
	
	let targetUrl = '';
	let forms = [];
	let error = '';
	let mode = '';
	let selectedFormIndex = null;
	let requestPreview = null;
	let attackType = '';

	async function scanTarget() {
	try {
		const response = await fetch(`${getApiBaseURL().trim()}/api/intruder/reconnaissance`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ url: targetUrl })
		});

		const data = await response.json();
		mode = data.mode;

		if (mode === 'html') {
			await fetchRequestPreview();
		}
		if (data.error) {
			error = data.error;
			return;
		}

		if (data.forms && data.forms.length > 0) {
			forms = data.forms;
			mode = data.mode;
			error = '';
			modeStore.set(mode);
			targetUrlStore.set(targetUrl);

		} else {
			if (data.mode === 'json' || data.mode === 'url') {
				modeStore.set(mode);
				targetUrlStore.set(targetUrl);
				goto(`/intruder/configure?noForm=true`);
			} else {
				error = "Unknown or unsupported mode.";
			}
		}
	} catch (err) {
		error = "Failed to connect to backend.";
		console.error(err);
	}
}

	async function fetchRequestPreview() {
		try {
			const res = await fetch(`${getApiBaseURL()}/api/intruder/preview_request`);
			if (!res.ok) {
				const data = await res.json();
				console.error("Error:", data);
				alert(data.detail || "Failed to get request preview");
				return;
			}
			requestPreview = await res.json();
		} catch (err) {
			console.error('Failed to fetch preview:', err);
		}
	}

	async function sendSelectedForm() {
		if (selectedFormIndex === null) return;

		const res = await fetch(`${getApiBaseURL()}/api/intruder/select_form`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ index: selectedFormIndex })
		});

		if (res.ok) {
			targetUrlStore.set(targetUrl);
			modeStore.set(mode);
			goto(`/intruder/configure?formIndex=${selectedFormIndex}&noForm=false`);
		} else {
			alert('Failed to select form.');
		}
	}
</script>

<div class="pt-6 pb-6 max-w-4xl mx-auto" style="padding-left:100px;padding-right:100px;">

	<div class="space-y-6">
		<div>
			<label for="targetUrl" class="block text-sm font-medium text-gray-800 mb-1 dark:text-foreground">
				Target URL <span class="text-red-500">*</span>
			</label>
			<input
				id="targetUrl"
				class="input"
				type="text"
				placeholder="https://juice-shop.herokuapp.com"
				bind:value={targetUrl}
			/>
		</div>
		<!-- 
		
		<!-- <button variant="outline" type="button"class="bg-cyan-500 text-white px-4 py-2 rounded transition-colors duration-100 ease-in-out hover:bg-gray-400" on:click={scanTarget}>
			Scan
		</button> -->
		<Button 
			type="button" 
			variant="outline" 
			size="default" 
			onclick={scanTarget} 
			class="bg-cyan-500 var(--foreground) px-4 py-2 rounded transition-colors duration-100 ease-in-out hover:bg-gray-400"
			>
			scan
		</Button>

		{#if error}
			<p class="text-red-500 mt-2">{error}</p>
		{/if}

		<!-- Results -->
		{#if forms.length > 0}
			<div class="mt-6">
				<h3 class="font-semibold text-lg mb-2 dark:text-foreground">Forms Found:</h3>
				{#each forms as form, i}
					<div class="border border-gray-300 p-4 rounded mb-4 dark:bg-background3 dark:text-background3-foreground">
						<label class="flex items-center space-x-2">
							<input
								type="radio"
								name="formSelector"
								bind:group={selectedFormIndex}
								value={i}
							/>
							<span class="font-semibold">Form {i}</span>
						</label>

						<p><b>Action:</b> {form.action}</p>
						<p><b>Method:</b> {form.method.toUpperCase()}</p>

						<table class="w-full mt-2 text-sm border border-gray-300 rounded ">
							<thead class="bg-gray-100 text-left">
								<tr>
									<th class="px-4 py-2 border-b dark:bg-accent">Name</th>
									<th class="px-4 py-2 border-b dark:bg-accent">Type</th>
								</tr>
							</thead>
							<tbody>
								{#each form.fields as field}
									<tr>
										<td class="px-4 py-2 border-b">{field.name || '(no name)'}</td>
										<td class="px-4 py-2 border-b">{field.type || 'text'}</td>
									</tr>
								{/each}
							</tbody>
						</table>
					</div>
				{/each}

				{#if selectedFormIndex !== null}
					<p class="mt-2 text-green-700 dark:text-accent2">
						Selected Form: {selectedFormIndex}
					</p>
				{/if}

				<!-- <button variant="outline" on:click={sendSelectedForm} class="b-start mt-4 outline ">
					Select Form
				</button> -->

				<Button 
				type="button" 
				variant="outline" 
				size="default" 
				onclick={sendSelectedForm} 
				class="bg-cyan-500 var(--foreground) px-4 py-2 rounded transition-colors duration-100 ease-in-out hover:bg-gray-400"
				>
				Select Form
			</Button>

				<!-- {#if requestPreview}
					<h3 class="mt-6 font-semibold text-lg">HTTP Request Preview</h3>
					<pre class="bg-gray-100 text-sm p-4 rounded overflow-x-auto">
URL: {requestPreview.url}
Method: {requestPreview.method}
Headers: {JSON.stringify(requestPreview.headers, null, 2)}

Sample Body:
{JSON.stringify(requestPreview.sample_body, null, 2)}
					</pre>
				{/if} -->
			</div>
		{/if}
	</div>
</div>

<style lang="postcss">
	@reference "tailwindcss";

	.input {
		@apply block w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-black/80 focus:border-black/80 transition;
	}
</style>
