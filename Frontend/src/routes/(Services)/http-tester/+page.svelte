<script>
	import { enhance } from '$app/forms';
	import RequestBuilder from '$lib/components/ui/request-builder/RequestBuilder.svelte';
	import ResponsePanel from '$lib/components/ui/response-panel/ResponsePanel.svelte';

	let response = null;
	let hideCodes = [];
	let showOnlyCodes = [];

	let formRef;
	let builderRef; // for calling .refreshRawRequest()
	let activeTab = 'request';

	let isLoading = false;

	async function handleResult({ result }) {
		const res = await result;

		// Treat both transport failures and JSON error payloads as errors
		if (res?.type === 'failure' || res?.data?.error) {
			response = { error: res.data?.error ?? res.statusText };
			// Only regenerate raw if coming from the form
			if (activeTab === 'request') {
				builderRef?.refreshRawRequest();
			}
			activeTab = 'raw';
			return;
		}

		const data = res.data;
		console.log('🎯 Successful response, triggering raw build...');

		response = {
			status: data.status_code ?? 0,
			statusText: data.statusText ?? 'OK',
			headers: data.headers ?? {},
			cookies: data.cookies ?? {},
			body: data.body ?? '',
			time: data.time ?? null,
			size: data.size ?? null
		};

		// Regenerate raw HTTP preview only if we sent from the form
		if (activeTab === 'request') {
			builderRef?.refreshRawRequest();
		}
		activeTab = 'raw';
	}

	// Hook into form handling
	const submitEnhance = (form) => {
		return async ({ result }) => {
			isLoading = true;

			await handleResult({ result });

			isLoading = false;
		};
	};
</script>

<form
	method="POST"
	use:enhance={submitEnhance}
	bind:this={formRef}
	on:submit={(e) => {
		isLoading = true; // Set here so the DOM updates *before* the fetch starts
		builderRef?.onSubmit(e);
	}}
	class="flex h-screen w-full items-center justify-center"
>
	<input type="hidden" name="mode" bind:value={activeTab} />

	<div class="flex h-[65vh] w-full max-w-6xl gap-4">
		<div class="h-full w-1/2">
			<RequestBuilder bind:this={builderRef} {formRef} bind:activeTab />
		</div>
		<div class="h-full w-1/2">
			<ResponsePanel {response} {hideCodes} {showOnlyCodes} {isLoading} />
		</div>
	</div>
</form>
