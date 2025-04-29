<script context="module">
	// Prevent Prism from running on the server
	export const ssr = false;
</script>

<script>
	import { enhance } from '$app/forms';
	import RequestBuilder from '$lib/components/ui/request-builder/RequestBuilder.svelte';
	import ResponsePanel from '$lib/components/ui/response-panel/ResponsePanel.svelte';

	let response = null;
	let hideCodes = [];
	let showOnlyCodes = [];
	let isLoading = false;

	let formRef;
	let builderRef;
	let activeTab = 'request';

	async function handleResult({ result }) {
		const res = await result;

		if (res?.type === 'failure' || res?.data?.error) {
			response = { error: res.data?.error ?? res.statusText };
			if (activeTab === 'request') builderRef?.refreshRawRequest();
			activeTab = 'raw';
			return;
		}

		const data = res.data;
		response = {
			status: data.status_code ?? 0,
			statusText: data.statusText ?? 'OK',
			headers: data.headers ?? {},
			cookies: data.cookies ?? {},
			body: data.body ?? '',
			time: data.time ?? null,
			size: data.size ?? null
		};

		console.log('▶️ response payload:', data);

		if (activeTab === 'request') builderRef?.refreshRawRequest();
		activeTab = 'raw';
	}

	const submitEnhance =
		() =>
		async ({ result }) => {
			isLoading = true;
			await handleResult({ result });
			isLoading = false;
		};
</script>

<svelte:head>
	<!-- Prism theme + line-numbers plugin CSS, loaded only on this route -->
	<link rel="stylesheet" href="https://unpkg.com/prismjs@1.29.0/themes/prism-tomorrow.css" />
	<link
		rel="stylesheet"
		href="https://unpkg.com/prismjs@1.29.0/plugins/line-numbers/prism-line-numbers.css"
	/>
</svelte:head>

<form
	method="POST"
	use:enhance={submitEnhance}
	bind:this={formRef}
	on:submit={(e) => {
		isLoading = true; // show spinner immediately
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
