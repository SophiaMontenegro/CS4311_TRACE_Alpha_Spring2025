<script>
	import { goto } from '$app/navigation';

	let targetUrl = '';
	let attackType = '';
	let header = '';
	let payloads = '';
	let injectionPoints = '';
	let hideStatusCodes = '';
	let showOnlyStatusCodes = '';
	let proxy = '';
	let additionalParams = '';


	function handleSubmit() {
		const payload = {
			targetUrl,
			attackType,
			header,
			payloads,
			injectionPoints,
			hideStatusCodes,
			showOnlyStatusCodes,
			proxy,
			additionalParams
		};

		console.log('Sending:', payload);

		const query = new URLSearchParams(payload).toString();

		goto(`/intruder/scan?${query}`);
	}
</script>

<!-- So for anyone that is modifying this part
 please make sure to make work the handle submit and sends it tothe backend!!!!!!!-->

<div class="pt-6 pb-6 max-w-4xl mx-auto" style="padding-left:100px;padding-right: 100px;">
	<form class="space-y-6" on:submit|preventDefault={handleSubmit}>

		<div>
			<label for="targetUrl" class="block text-sm font-medium text-gray-800 mb-1">Target URL <span class="text-red-500">*</span></label>
			<input id="targetUrl" class="input" type="text" placeholder="https://juice-shop.herokuapp.com" bind:value={targetUrl} />
		</div>

		<div>
			<label for="attackType" class="block text-sm font-medium text-gray-800 mb-1">Attack Type</label>
			<input id="attackType" class="input" type="text" placeholder="Sniper" bind:value={attackType} />
		</div>

		<div>
			<label for="header" class="block text-sm font-medium text-gray-800 mb-1">Header</label>
			<input id="header" class="input text-gray-400" type="text" placeholder="application/json" bind:value={header} />
		</div>

		<div>
			<label for="payloads" class="block text-sm font-medium text-gray-800 mb-1">Payloads</label>
			<input id="payloads" class="input" type="text" placeholder="?id =, ?username" bind:value={payloads} />
		</div>

		<div>
			<label for="injectionPoints" class="block text-sm font-medium text-gray-800 mb-1">Injection Points</label>
			<input id="injectionPoints" class="input" type="text" placeholder="?id =, ?username" bind:value={injectionPoints} />
		</div>

		<div>
			<label for="hideStatusCodes" class="block text-sm font-medium text-gray-800 mb-1">Hide Status Code</label>
			<input id="hideStatusCodes" class="input" type="text" placeholder="403, etc." bind:value={hideStatusCodes} />
		</div>

		<div>
			<label for="showOnlyStatusCodes" class="block text-sm font-medium text-gray-800 mb-1">Show Only Status Code</label>
			<input id="showOnlyStatusCodes" class="input" type="text" placeholder="200, 500, etc." bind:value={showOnlyStatusCodes} />
		</div>

		<div>
			<label for="proxy" class="block text-sm font-medium text-gray-800 mb-1">Proxy</label>
			<input id="proxy" class="input" type="text" placeholder="https://proxy.example.com:3128" bind:value={proxy} />
		</div>

		<div>
			<label for="additionalParams" class="block text-sm font-medium text-gray-800 mb-1">Additional Parameters (if applicable)</label>
			<input id="additionalParams" class="input" type="text" placeholder="NULL" bind:value={additionalParams} />
		</div>

		<button type="submit" class="b-start">
		Start Attack
		</button>
	</form>
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
