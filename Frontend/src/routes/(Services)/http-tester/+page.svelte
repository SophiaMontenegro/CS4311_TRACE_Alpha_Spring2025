<script>
	import { enhance } from '$app/forms';
	import RequestBuilder from '$lib/components/ui/request-builder/RequestBuilder.svelte';
	import ResponsePanel from '$lib/components/ui/response-panel/ResponsePanel.svelte';
	import { onMount } from 'svelte';

	let response = null;
	let hideCodes = [];
	let showOnlyCodes = [];
	let isLoading = false;

	let formRef;
	let builderRef;
	let activeTab = 'request';

	let currentProjectName = 'Unnamed Project';
	let apiBaseURL = 'http://127.0.0.1:8000';

	onMount(() => {
		currentProjectName = localStorage.getItem('current_project_name') || 'Unnamed Project';
		apiBaseURL = localStorage.getItem('apiBaseURL') || apiBaseURL;
	});

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
			status: data.status ?? data.status_code ?? 0,
			statusText: data.statusText ?? 'OK',
			headers: data.headers ?? {},
			cookies: data.cookies ?? {},
			body: data.body ?? '',
			time: data.time ?? null,
			size: data.size ?? null
		};

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
		builderRef?.onSubmit(e);
		// if client‐side validation passed, kick off the spinner
		if (!builderRef?.validationErrors?.length) {
			isLoading = true;
		}
	}}
	class="flex h-screen w-full items-center justify-center"
>
	<input type="hidden" name="mode" bind:value={activeTab} />

	<input type="hidden" name="currentProjectName" value={currentProjectName} />
	<input type="hidden" name="apiBaseURL" value={apiBaseURL} />

	<div class="flex h-[65vh] w-full max-w-6xl gap-4">
		<div class="h-full w-1/2">
			<RequestBuilder bind:this={builderRef} {formRef} bind:activeTab />
		</div>
		<div class="h-full w-1/2">
			<ResponsePanel {response} {hideCodes} {showOnlyCodes} {isLoading} />
		</div>
	</div>
</form>
