<script>
	let targetUrl = '';
	let forms = [];
	let error = '';
	let selectedFormIndex = null;
	

	async function sendSelectedForm() {
	if (selectedFormIndex === null) return;

	await fetch("http://localhost:8000/api/intruder/select_form", {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({ index: selectedFormIndex })
	});
}





	async function scanForms() {
		try {
			const response = await fetch('http://localhost:8000/api/intruder/parse_forms', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ url: targetUrl })
		});


			const data = await response.json();
			if (data.forms) {
				forms = data.forms;
				error = '';
			} else {
				error = data.error || 'Unexpected error';
			}
		} catch (err) {
			error = 'Failed to connect to backend.';
			console.error(err);
		}
	}
</script>

<div class="pt-6 pb-6 max-w-4xl mx-auto" style="padding-left:100px;padding-right:100px;">
	<!-- Target URL Input -->
	<div class="space-y-6">
		<div>
			<label for="targetUrl" class="block text-sm font-medium text-gray-800 mb-1">
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

		<!-- Scan Button -->
		<button type="button" class="b-start" on:click={scanForms}>
			Scan for Forms
		</button>

		{#if error}
			<p class="text-red-500 mt-2">{error}</p>
		{/if}

		<!-- Results -->
		{#if forms.length > 0}
			<div class="mt-6">
				<h3 class="font-semibold text-lg mb-2">Forms Found:</h3>
				{#each forms as form, i}
				<div class="border border-gray-300 p-4 rounded mb-4">
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

					<table class="w-full mt-2 text-sm border border-gray-300 rounded">
						<thead class="bg-gray-100 text-left">
							<tr>
								<th class="px-4 py-2 border-b">Name</th>
								<th class="px-4 py-2 border-b">Type</th>
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
			<p class="mt-2 text-green-700">
			 Selected Form: {selectedFormIndex}
			</p>
			{/if}
			
			</div>
			<button on:click={sendSelectedForm} class="b-start mt-4">
				Send Selected Form to Backend
			</button>
		{/if}
	</div>
</div>

<style lang="postcss">
	@reference "tailwindcss";

	.input {
		@apply block w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-black/80 focus:border-black/80 transition;
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
