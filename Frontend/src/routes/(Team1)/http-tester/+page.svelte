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

  async function handleResult({ result }) {
	const res = await result;

	if (res?.type === 'failure') {
		response = { error: res.statusText };
		builderRef?.refreshRawRequest(); 
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

	// ✅ After updating response, generate raw HTTP preview
	builderRef?.refreshRawRequest();
	activeTab = 'raw';
}

	// Hook into form handling
	const submitEnhance = (form) => {
		return async ({ result }) => handleResult({ result });
	};
</script>

<form
	method="POST"
	use:enhance={submitEnhance}
	bind:this={formRef}
	class="flex justify-center items-center w-full h-screen"
>
	<div class="flex gap-4 w-full max-w-6xl h-[65vh]">
		<div class="w-1/2 h-full">
			<RequestBuilder
				bind:this={builderRef}
				{formRef}
				bind:activeTab
			/>
		</div>
		<div class="w-1/2 h-full">
			<ResponsePanel
				{response}
				{hideCodes}
				{showOnlyCodes}
			/>
		</div>
	</div>
</form>
